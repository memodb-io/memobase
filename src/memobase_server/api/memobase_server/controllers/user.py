from ..models.utils import Promise
from ..models.database import User
from ..models.response import CODE, UserData, IdData
from ..connectors import Session


async def create_user(data: UserData) -> Promise[IdData]:
    with Session() as session:
        db_user = User(addional_fields=data.data)
        session.add(db_user)
        session.commit()
        return Promise.resolve(IdData(id=db_user.id))


async def get_user(user_id: str) -> Promise[UserData]:
    with Session() as session:
        db_user = session.query(User).filter_by(id=user_id).first()
        if db_user is None:
            return Promise.reject(CODE.NOT_FOUND, f"User {user_id} not found")
        return Promise.resolve(
            UserData(
                data=db_user.addional_fields,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
            )
        )


async def update_user(user_id: str, data: UserData) -> Promise[IdData]:
    with Session() as session:
        db_user = session.query(User).filter_by(id=user_id).first()
        if db_user is None:
            return Promise.reject(CODE.NOT_FOUND, f"User {user_id} not found")
        db_user.addional_fields = data.data
        session.commit()
        return Promise.resolve(IdData(id=db_user.id))


async def delete_user(user_id: str) -> Promise[None]:
    with Session() as session:
        db_user = session.query(User).filter_by(id=user_id).first()
        if db_user is None:
            return Promise.reject(CODE.NOT_FOUND, f"User {user_id} not found")
        session.delete(db_user)
        session.commit()
        return Promise.resolve(None)
