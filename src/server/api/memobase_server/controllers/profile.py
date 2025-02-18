from pydantic import ValidationError
from ..models.utils import Promise
from ..models.database import GeneralBlob, UserProfile
from ..models.response import CODE, IdData, IdsData, UserProfilesData
from ..connectors import Session, get_redis_client
from ..utils import get_encoded_tokens
from ..env import LOG, CONFIG


async def truncate_profiles(
    profiles: UserProfilesData,
    prefer_topics: list[str] = None,
    topk: int = None,
    max_token_size: int = None,
) -> Promise[UserProfilesData]:
    profiles.profiles.sort(key=lambda p: p.updated_at, reverse=True)
    if prefer_topics:
        priority_weights = {t: i for i, t in enumerate(prefer_topics)}
        priority_profiles = []
        non_priority_profiles = []
        for p in profiles.profiles:
            if p.attributes.get("topic") in priority_weights:
                priority_profiles.append(p)
            else:
                non_priority_profiles.append(p)
        priority_profiles.sort(
            key=lambda p: priority_weights[p.attributes.get("topic")]
        )
        profiles.profiles = priority_profiles + non_priority_profiles
    if topk:
        profiles.profiles = profiles.profiles[:topk]
    if max_token_size:
        current_length = 0
        for max_i, p in enumerate(profiles.profiles):
            current_length += len(get_encoded_tokens(p.content))
            if current_length > max_token_size:
                break
        profiles.profiles = profiles.profiles[: max_i + 1]
    return Promise.resolve(profiles)


async def get_user_profiles(user_id: str, project_id: str) -> Promise[UserProfilesData]:
    async with get_redis_client() as redis_client:
        user_profiles = await redis_client.get(
            f"user_profiles::{project_id}::{user_id}"
        )
        if user_profiles:
            try:
                return Promise.resolve(
                    UserProfilesData.model_validate_json(user_profiles)
                )
            except ValidationError as e:
                LOG.error(f"Invalid user profiles: {e}")
                await redis_client.delete(f"user_profiles::{project_id}::{user_id}")
    with Session() as session:
        user_profiles = (
            session.query(UserProfile)
            .filter_by(user_id=user_id, project_id=project_id)
            .order_by(UserProfile.updated_at.desc())
            .all()
        )
        results = []
        for up in user_profiles:
            results.append(
                {
                    "id": up.id,
                    "content": up.content,
                    "attributes": up.attributes,
                    "created_at": up.created_at,
                    "updated_at": up.updated_at,
                }
            )
    return_profiles = UserProfilesData(profiles=results)
    async with get_redis_client() as redis_client:
        await redis_client.set(
            f"user_profiles::{project_id}::{user_id}",
            return_profiles.model_dump_json(),
            ex=CONFIG.cache_user_profiles_ttl,
        )
    return Promise.resolve(return_profiles)


async def add_user_profiles(
    user_id: str,
    project_id: str,
    profiles: list[str],
    attributes: list[dict],
) -> Promise[IdsData]:
    assert len(profiles) == len(
        attributes
    ), "Length of profiles, attributes must be equal"
    with Session() as session:
        db_profiles = [
            UserProfile(
                user_id=user_id, project_id=project_id, content=content, attributes=attr
            )
            for content, attr in zip(profiles, attributes)
        ]
        session.add_all(db_profiles)
        session.commit()
        profile_ids = [profile.id for profile in db_profiles]
    async with get_redis_client() as redis_client:
        await redis_client.delete(f"user_profiles::{project_id}::{user_id}")
    return Promise.resolve(IdsData(ids=profile_ids))


async def update_user_profiles(
    user_id: str,
    project_id: str,
    profile_ids: list[str],
    contents: list[str],
    attributes: list[dict | None],
):
    assert len(profile_ids) == len(
        contents
    ), "Length of profile_ids, contents must be equal"
    assert len(profile_ids) == len(
        attributes
    ), "Length of profile_ids, attributes must be equal"
    with Session() as session:
        db_profiles = []
        for profile_id, content, attribute in zip(profile_ids, contents, attributes):
            db_profile = (
                session.query(UserProfile)
                .filter_by(id=profile_id, user_id=user_id, project_id=project_id)
                .one_or_none()
            )
            if db_profile is None:
                LOG.error(f"Profile {profile_id} not found for user {user_id}")
                continue
            db_profile.content = content
            if attribute is not None:
                db_profile.attributes = attribute
            db_profiles.append(profile_id)
        session.commit()
    async with get_redis_client() as redis_client:
        await redis_client.delete(f"user_profiles::{project_id}::{user_id}")
    return Promise.resolve(IdsData(ids=db_profiles))


async def delete_user_profile(
    user_id: str, project_id: str, profile_id: str
) -> Promise[None]:
    with Session() as session:
        db_profile = (
            session.query(UserProfile)
            .filter_by(id=profile_id, user_id=user_id, project_id=project_id)
            .one_or_none()
        )
        if db_profile is None:
            return Promise.reject(
                CODE.NOT_FOUND, f"Profile {profile_id} not found for user {user_id}"
            )
        session.delete(db_profile)
        session.commit()
    async with get_redis_client() as redis_client:
        await redis_client.delete(f"user_profiles::{project_id}::{user_id}")
    return Promise.resolve(None)


async def delete_user_profiles(
    user_id: str, project_id: str, profile_ids: list[str]
) -> Promise[None]:
    with Session() as session:
        session.query(UserProfile).filter(
            UserProfile.id.in_(profile_ids),
            UserProfile.user_id == user_id,
            UserProfile.project_id == project_id,
        ).delete(synchronize_session=False)
        session.commit()
    async with get_redis_client() as redis_client:
        await redis_client.delete(f"user_profiles::{project_id}::{user_id}")
    return Promise.resolve(None)
