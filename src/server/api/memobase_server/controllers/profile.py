from ..models.utils import Promise
from ..models.database import GeneralBlob, UserProfile
from ..models.response import CODE, IdData, IdsData, UserProfilesData
from ..connectors import Session


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
    assert (
        len(profiles) == len(related_blobs) == len(attributes)
    ), "Length of profiles, attributes and related_blobs must be equal"
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
    content: str,
    attributes: dict = None,
    related_blobs: list[str] = None,
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

        if attributes is not None:
            db_profile.attributes = attributes
        if related_blobs is not None:
            db_profile.related_blobs = (
                session.query(GeneralBlob)
                .filter(GeneralBlob.id.in_(related_blobs))
                .all()
            )
        session.commit()
        return Promise.resolve(IdData(id=db_profile.id))


async def delete_user_profile(user_id: str, profile_id: str) -> Promise[None]:
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
        session.delete(db_profile)
        session.commit()
    return Promise.resolve(None)
