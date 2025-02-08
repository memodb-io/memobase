from pydantic import ValidationError
from ..models.database import UserEvent
from ..models.response import UserEventData, UserEventsData, EventData
from ..models.utils import Promise, CODE
from ..connectors import Session


async def get_user_events(
    user_id: str, project_id: str, topk: int = 10
) -> Promise[UserEventsData]:
    with Session() as session:
        user_events = (
            session.query(UserEvent)
            .filter_by(user_id=user_id, project_id=project_id)
            .order_by(UserEvent.created_at.desc())
            .limit(topk)
            .all()
        )
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
        return Promise.resolve(UserEventsData(events=results))


async def append_user_event(
    user_id: str, project_id: str, event_data: dict
) -> Promise[None]:
    try:
        validated_event = EventData(**event_data)
    except ValidationError as e:
        return Promise.reject(
            CODE.INVALID_REQUEST,
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
