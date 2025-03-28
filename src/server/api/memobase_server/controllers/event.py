from pydantic import ValidationError
from ..models.database import UserEvent
from ..models.response import UserEventData, UserEventsData, EventData
from ..models.utils import Promise, CODE
from ..connectors import Session
from ..utils import get_encoded_tokens, event_str_repr


async def get_user_events(
    user_id: str,
    project_id: str,
    topk: int = 10,
    max_token_size: int = None,
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
    if max_token_size is not None:
        c_tokens = 0
        truncated_results = []
        for r in events.events:
            c_tokens += len(get_encoded_tokens(event_str_repr(r)))
            if c_tokens > max_token_size:
                break
            truncated_results.append(r)
        results = truncated_results
        events.events = results
    return Promise.resolve(events)


async def append_user_event(
    user_id: str, project_id: str, event_data: dict
) -> Promise[None]:
    try:
        validated_event = EventData(**event_data)
    except ValidationError as e:
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR,
            f"Invalid event data: {str(e)}",
        )
    with Session() as session:
        user_event = UserEvent(
            user_id=user_id,
            project_id=project_id,
            event_data=validated_event.model_dump(),
        )
        session.add(user_event)
        session.commit()
    return Promise.resolve(None)


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
