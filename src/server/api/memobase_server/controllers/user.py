from ..models.utils import Promise
from ..models.database import User, GeneralBlob, UserProfile
from ..models.response import CODE, UserData, IdData, IdsData, UserProfilesData
from ..connectors import Session


async def create_user(data: UserData) -> Promise[IdData]:
    with Session() as session:
        db_user = User(additional_fields=data.data)
        if data.id is not None:
            db_user.id = str(data.id)
        session.add(db_user)
        session.commit()
        return Promise.resolve(IdData(id=db_user.id))


async def get_user(user_id: str) -> Promise[UserData]:
    with Session() as session:
        db_user = session.query(User).filter_by(id=user_id).one_or_none()
        if db_user is None:
            return Promise.reject(CODE.NOT_FOUND, f"User {user_id} not found")
        return Promise.resolve(
            UserData(
                data=db_user.additional_fields,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
            )
        )


async def update_user(user_id: str, data: UserData) -> Promise[IdData]:
    with Session() as session:
        db_user = session.query(User).filter_by(id=user_id).one_or_none()
        if db_user is None:
            return Promise.reject(CODE.NOT_FOUND, f"User {user_id} not found")
        db_user.additional_fields = data.data
        session.commit()
        return Promise.resolve(IdData(id=db_user.id))


async def delete_user(user_id: str) -> Promise[None]:
    with Session() as session:
        db_user = session.query(User).filter_by(id=user_id).one_or_none()
        if db_user is None:
            return Promise.reject(CODE.NOT_FOUND, f"User {user_id} not found")
        session.delete(db_user)
        session.commit()
        return Promise.resolve(None)


async def get_user_all_blobs(user_id: str) -> Promise[IdsData]:
    with Session() as session:
        user_blobs = (
            session.query(GeneralBlob.id)
            .filter_by(user_id=user_id)
            .order_by(GeneralBlob.created_at)
            .all()
        )
        if user_blobs is None:
            return Promise.reject(CODE.NOT_FOUND, f"User {user_id} not found")
        return Promise.resolve(IdsData(ids=[blob.id for blob in user_blobs]))
