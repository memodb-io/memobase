from ..models.utils import Promise
from ..models.database import User, GeneralBlob, UserProfile
from ..models.response import CODE, UserData, IdData, IdsData, UserProfilesData
from ..connectors import Session


async def create_user(data: UserData) -> Promise[IdData]:
    with Session() as session:
        db_user = User(additional_fields=data.data)
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


async def get_user_profiles(user_id: str) -> Promise[UserProfilesData]:
    with Session() as session:
        user_profiles = (
            session.query(UserProfile)
            .filter_by(user_id=user_id)
            .order_by(UserProfile.updated_at)
            .all()
        )
        results = []
        for up in user_profiles:
            results.append(
                {
                    "id": up.id,
                    "content": up.content,
                    "attributes": up.attributes,
                    "related_blobs": [blob.id for blob in up.related_blobs],
                    "created_at": up.created_at,
                    "updated_at": up.updated_at,
                }
            )
        return Promise.resolve(UserProfilesData(profiles=results))


async def add_user_profiles(
    user_id: str,
    profiles: list[str],
    attributes: list[dict],
    related_blobs: list[list[str]],
) -> Promise[IdsData]:
    assert len(profiles) == len(
        related_blobs
    ), "Length of profiles and related_blobs must be equal"
    with Session() as session:
        db_profiles = [
            UserProfile(user_id=user_id, content=content, attributes=attr)
            for content, attr in zip(profiles, attributes)
        ]
        session.add_all(db_profiles)
        for dp, rb_ids in zip(db_profiles, related_blobs):
            if not len(rb_ids):
                continue
            # TODO: this is not efficient, find a way to only use blob_ids to link
            dp.related_blobs = (
                session.query(GeneralBlob).filter(GeneralBlob.id.in_(rb_ids)).all()
            )
        session.commit()
        return Promise.resolve(IdsData(ids=[profile.id for profile in db_profiles]))


async def update_user_profile(
    user_id: str,
    profile_id: str,
    attributes: dict,
    content: str,
    related_blobs: list[str],
):
    with Session() as session:
        db_profile = (
            session.query(UserProfile)
            .filter_by(id=profile_id, user_id=user_id)
            .one_or_none()
        )
        if db_profile is None:
            return Promise.reject(
                CODE.NOT_FOUND, f"Profile {profile_id} not found for user {user_id}"
            )
        db_profile.content = content
        db_profile.attributes = attributes
        db_profile.related_blobs = (
            session.query(GeneralBlob).filter(GeneralBlob.id.in_(related_blobs)).all()
        )
        session.commit()
        return Promise.resolve(IdData(id=db_profile.id))
