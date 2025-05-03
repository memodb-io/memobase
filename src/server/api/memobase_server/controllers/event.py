from pydantic import ValidationError
from ..models.database import UserEvent
from ..models.response import UserEventData, UserEventsData, EventData
from ..models.utils import Promise, CODE
from ..connectors import Session
from ..utils import get_encoded_tokens, event_str_repr, event_embedding_str

from ..llms.embeddings import get_embedding
from datetime import timedelta
from sqlalchemy import desc, select
from sqlalchemy.sql import func
from ..env import LOG, CONFIG


async def get_user_events(
    user_id: str,
    project_id: str,
    topk: int = 10,
    need_summary: bool = False,
) -> Promise[UserEventsData]:
    with Session() as session:
        query = session.query(UserEvent).filter_by(
            user_id=user_id, project_id=project_id
        )
        if need_summary:
            query = query.filter(
                UserEvent.event_data.contains({"event_tip": None}).is_(False)
            ).filter(UserEvent.event_data.has_key("event_tip"))
        user_events = query.order_by(UserEvent.created_at.desc()).limit(topk).all()
        if user_events is None:
            return Promise.reject(
                CODE.NOT_FOUND,
                f"No user events found for user {user_id}",
            )
        results = [
            {
                "id": ue.id,
                "event_data": ue.event_data,
                "created_at": ue.created_at,
                "updated_at": ue.updated_at,
            }
            for ue in user_events
        ]
    events = UserEventsData(events=results)
    return Promise.resolve(events)


async def truncate_events(
    events: UserEventsData,
    max_token_size: int | None,
) -> Promise[UserEventsData]:
    if max_token_size is None:
        return Promise.resolve(events)
    c_tokens = 0
    truncated_results = []
    for r in events.events:
        c_tokens += len(get_encoded_tokens(event_str_repr(r)))
        if c_tokens > max_token_size:
            break
        truncated_results.append(r)
    events.events = truncated_results
    return Promise.resolve(events)


async def append_user_event(
    user_id: str, project_id: str, event_data: dict
) -> Promise[str]:
    try:
        validated_event = EventData(**event_data)
    except ValidationError as e:
        LOG.error(f"Invalid event data: {str(e)}")
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR,
            f"Invalid event data: {str(e)}",
        )

    if CONFIG.enable_event_embedding:
        event_data_str = event_embedding_str(validated_event)
        embedding = await get_embedding(
            project_id,
            [event_data_str],
            phase="document",
            model=CONFIG.embedding_model,
        )
        if not embedding.ok():
            LOG.error(f"Failed to get embeddings: {embedding.msg()}")
            embedding = [None]
        else:
            embedding = embedding.data()
            embedding_dim_current = embedding.shape[-1]
            if embedding_dim_current != CONFIG.embedding_dim:
                LOG.error(
                    f"Embedding dimension mismatch! Expected {CONFIG.embedding_dim}, got {embedding_dim_current}."
                )
                embedding = [None]
    else:
        embedding = [None]

    with Session() as session:
        user_event = UserEvent(
            user_id=user_id,
            project_id=project_id,
            event_data=validated_event.model_dump(),
            embedding=embedding[0],
        )
        session.add(user_event)
        session.commit()
        eid = user_event.id
    return Promise.resolve(eid)


async def delete_user_event(
    user_id: str, project_id: str, event_id: str
) -> Promise[None]:
    with Session() as session:
        user_event = (
            session.query(UserEvent)
            .filter_by(user_id=user_id, project_id=project_id, id=event_id)
            .first()
        )
        if user_event is None:
            return Promise.reject(
                CODE.NOT_FOUND,
                f"User event {event_id} not found",
            )
        session.delete(user_event)
        session.commit()
    return Promise.resolve(None)


async def update_user_event(
    user_id: str, project_id: str, event_id: str, event_data: dict
) -> Promise[None]:
    try:
        EventData(**event_data)
    except ValidationError as e:
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR,
            f"Invalid event data: {str(e)}",
        )
    need_to_update = {k: v for k, v in event_data.items() if v is not None}
    with Session() as session:
        user_event = (
            session.query(UserEvent)
            .filter_by(user_id=user_id, project_id=project_id, id=event_id)
            .first()
        )
        if user_event is None:
            return Promise.reject(
                CODE.NOT_FOUND,
                f"User event {event_id} not found",
            )
        new_events = dict(user_event.event_data)
        new_events.update(need_to_update)

        user_event.event_data = new_events
        session.commit()
    return Promise.resolve(None)


async def search_user_events(
    user_id: str,
    project_id: str,
    query: str,
    topk: int = 10,
    similarity_threshold: float = 0.6,
    time_range_in_days: int = 21,
) -> Promise[UserEventsData]:
    if not CONFIG.enable_event_embedding:
        return Promise.reject(
            CODE.NOT_IMPLEMENTED,
            "Event embedding is not enabled",
        )

    query_embeddings = await get_embedding(
        project_id, [query], phase="query", model=CONFIG.embedding_model
    )
    if not query_embeddings.ok():
        LOG.error(f"Failed to get embeddings: {query_embeddings.msg()}")
        return query_embeddings
    query_embedding = query_embeddings.data()[0]

    stmt = (
        select(
            UserEvent,
            (1 - UserEvent.embedding.cosine_distance(query_embedding)).label(
                "similarity"
            ),
        )
        .where(UserEvent.user_id == user_id, UserEvent.project_id == project_id)
        .where(UserEvent.created_at > func.now() - timedelta(days=time_range_in_days))
        .where(
            (1 - UserEvent.embedding.cosine_distance(query_embedding))
            > similarity_threshold
        )
        .order_by(desc("similarity"))
        .limit(topk)
    )

    with Session() as session:
        # Use .all() instead of .scalars().all() to get both columns
        result = session.execute(stmt).all()
        user_events: list[UserEventData] = []
        for row in result:
            user_event: UserEvent = row[0]  # UserEvent object
            similarity: float = row[1]  # similarity value
            user_events.append(
                UserEventData(
                    id=user_event.id,
                    event_data=user_event.event_data,
                    created_at=user_event.created_at,
                    updated_at=user_event.updated_at,
                    similarity=similarity,
                )
            )

        # Create UserEventsData with the events
        user_events_data = UserEventsData(events=user_events)
        LOG.info(f"Event Query: {query}")

    return Promise.resolve(user_events_data)
