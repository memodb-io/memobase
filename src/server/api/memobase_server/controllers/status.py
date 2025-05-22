from pydantic import ValidationError
from ..models.utils import Promise
from ..models.database import UserStatus
from ..models.response import CODE, UserStatusesData, UserStatusData, IdData
from ..connectors import Session


async def get_user_statuses(
    user_id: str, project_id: str, type: str, page: int = 1, page_size: int = 10
) -> Promise[UserStatusesData]:
    with Session() as session:
        status = (
            session.query(UserStatus)
            .filter_by(user_id=user_id, project_id=project_id, type=type)
            .order_by(UserStatus.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        if status is None:
            return Promise.resolve(UserStatusesData(statuses=[]))
        data = [
            {
                "id": s.id,
                "type": s.type,
                "attributes": s.attributes,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            }
            for s in status
        ]
        return Promise.resolve(UserStatusesData(statuses=data))


async def append_user_status(
    user_id: str, project_id: str, type: str, attributes: dict
) -> Promise[IdData]:
    with Session() as session:
        status = UserStatus(
            user_id=user_id, project_id=project_id, type=type, attributes=attributes
        )
        session.add(status)
        session.commit()
        return Promise.resolve(IdData(id=status.id))
