from pydantic import ValidationError
from ..models.database import UserEvent, UserEventGist
from ..models.response import UserEventData, UserEventsData, EventData
from ..models.utils import Promise, CODE
from ..connectors import Session
from ..utils import get_encoded_tokens, event_str_repr, event_embedding_str

from ..llms.embeddings import get_embedding
from datetime import timedelta
from sqlalchemy import desc, select
from sqlalchemy.sql import func
from ..env import TRACE_LOG, CONFIG


async def get_user_events(
    user_id: str,
    project_id: str,
    topk: int = 10,
    need_summary: bool = False,
    time_range_in_days: int = 21,
) -> Promise[UserEventsData]:
    with Session() as session:
        query = (
            session.query(UserEvent)
            .filter_by(user_id=user_id, project_id=project_id)
            .filter(
                UserEvent.created_at > (func.now() - timedelta(days=time_range_in_days))
            )
        )
        # Abort this parameter because the summary is moved to gist
        # if need_summary:
        #     query = query.filter(
        #         UserEvent.event_data.contains({"event_tip": None}).is_(False)
        #     ).filter(UserEvent.event_data.has_key("event_tip"))
        user_events = query.order_by(UserEvent.created_at.desc()).limit(topk).all()
        if user_events is None:
            return Promise.resolve(UserEventsData(events=[]))
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
        TRACE_LOG.error(
            project_id,
            user_id,
            f"Invalid event data: {str(e)}",
        )
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
            TRACE_LOG.error(
                project_id,
                user_id,
                f"Failed to get embeddings: {embedding.msg()}",
            )
            embedding = [None]
        else:
            embedding = embedding.data()
            embedding_dim_current = embedding.shape[-1]
            if embedding_dim_current != CONFIG.embedding_dim:
                TRACE_LOG.error(
                    project_id,
                    user_id,
                    f"Embedding dimension mismatch! Expected {CONFIG.embedding_dim}, got {embedding_dim_current}.",
                )
                embedding = [None]
    else:
        embedding = [None]

    event_gist_dbs = []
    if validated_event.event_tip is not None:
        event_gists = validated_event.event_tip.split("\n")
        event_gists = [l.strip() for l in event_gists if l.strip().startswith("-")]
        TRACE_LOG.info(
            project_id, user_id, f"Processing {len(event_gists)} event gists"
        )
        if CONFIG.enable_event_embedding and len(event_gists) > 0:
            event_gists_embedding = await get_embedding(
                project_id,
                event_gists,
                phase="document",
                model=CONFIG.embedding_model,
            )
            if not event_gists_embedding.ok():
                TRACE_LOG.error(
                    project_id,
                    user_id,
                    f"Failed to get embeddings: {event_gists_embedding.msg()}",
                )
                event_gists_embedding = [None] * len(event_gists)
            else:
                event_gists_embedding = event_gists_embedding.data()
        else:
            event_gists_embedding = [None] * len(event_gists)
        for event_gist, event_gist_embedding in zip(event_gists, event_gists_embedding):
            event_gist_dbs.append(
                {
                    "gist_data": {"content": event_gist},
                    "embedding": event_gist_embedding,
                }
            )
    with Session() as session:
        user_event = UserEvent(
            user_id=user_id,
            project_id=project_id,
            event_data=validated_event.model_dump(),
            embedding=embedding[0],
        )
        session.add(user_event)
        for event_gist_data in event_gist_dbs:
            session.add(
                UserEventGist(
                    user_id=user_id,
                    project_id=project_id,
                    event_id=user_event.id,
                    gist_data=event_gist_data["gist_data"],
                    embedding=event_gist_data["embedding"],
                )
            )
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
    similarity_threshold: float = 0.2,
    time_range_in_days: int = 21,
) -> Promise[UserEventsData]:
    if not CONFIG.enable_event_embedding:
        TRACE_LOG.warning(
            project_id,
            user_id,
            "Event embedding is not enabled, skip search",
        )
        return Promise.reject(
            CODE.NOT_IMPLEMENTED,
            "Event embedding is not enabled",
        )

    query_embeddings = await get_embedding(
        project_id, [query], phase="query", model=CONFIG.embedding_model
    )
    if not query_embeddings.ok():
        TRACE_LOG.error(
            project_id,
            user_id,
            f"Failed to get embeddings: {query_embeddings.msg()}",
        )
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
        TRACE_LOG.info(
            project_id,
            user_id,
            f"Event Query: {query}",
        )

    return Promise.resolve(user_events_data)


async def filter_user_events(
    user_id: str,
    project_id: str,
    has_event_tag: list[str] = None,
    event_tag_equal: dict[str, str] = None,
    topk: int = 10,
) -> Promise[UserEventsData]:
    """
    Filter user events based on event tags.

    Args:
        user_id: User ID
        project_id: Project ID
        has_event_tag: List of tag names that must exist in the event (regardless of value)
        event_tag_equal: Dict of tag_name: tag_value pairs that must match exactly
        topk: Maximum number of events to return

    Returns:
        Promise containing filtered UserEventsData
    """
    with Session() as session:
        query = session.query(UserEvent).filter_by(
            user_id=user_id, project_id=project_id
        )

        # Apply tag filters if provided
        if has_event_tag or event_tag_equal:
            # Build filter conditions for events that have event_tags
            query = query.filter(UserEvent.event_data.has_key("event_tags"))
            query = query.filter(UserEvent.event_data["event_tags"].isnot(None))

            # Filter by tag existence (has_event_tag)
            if has_event_tag:
                for tag_name in has_event_tag:
                    # Check if any event_tag in the array has the specified tag name
                    query = query.filter(
                        UserEvent.event_data["event_tags"].op("@>")(
                            f'[{{"tag": "{tag_name}"}}]'
                        )
                    )

            # Filter by exact tag-value pairs (event_tag_equal)
            if event_tag_equal:
                for tag_name, tag_value in event_tag_equal.items():
                    # Check if any event_tag in the array has both the tag name and value
                    query = query.filter(
                        UserEvent.event_data["event_tags"].op("@>")(
                            f'[{{"tag": "{tag_name}", "value": "{tag_value}"}}]'
                        )
                    )

        user_events = query.order_by(UserEvent.created_at.desc()).limit(topk).all()

        if user_events is None:
            return Promise.resolve(UserEventsData(events=[]))

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
