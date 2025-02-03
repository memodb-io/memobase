import asyncio

from ....env import LOG
from ....models.blob import Blob
from ....models.utils import Promise
from ...profile import add_user_profiles, update_user_profiles, delete_user_profiles
from .extract import extract_topics
from .merge import merge_or_add_new_memos
from .summary import re_summary
from .organize import organize_profiles
from .types import MergeAddResult


async def process_blobs(
    user_id: str, project_id: str, blob_ids: list[str], blobs: list[Blob]
) -> Promise[None]:
    # 1. Extract patch profiles
    p = await extract_topics(user_id, project_id, blob_ids, blobs)
    if not p.ok():
        return p
    extracted_data = p.data()

    # 2. Merge it to thw whole profile
    p = await merge_or_add_new_memos(
        fact_contents=extracted_data["fact_contents"],
        fact_attributes=extracted_data["fact_attributes"],
        profiles=extracted_data["profiles"],
    )
    if not p.ok():
        return p
    profile_options = p.data()

    # 3. Check if we need to organize profiles
    p = await organize_profiles(profile_options)
    if not p.ok():
        LOG.error(f"Failed to organize profiles: {p.msg()}")

    # 4. Re-summary profiles if any slot is too big
    p = await re_summary(
        add_profile=profile_options["add"],
        update_profile=profile_options["update"],
    )
    if not p.ok():
        LOG.error(f"Failed to re-summary profiles: {p.msg()}")

    # DB commit
    ps = await asyncio.gather(
        exe_user_profile_add(user_id, project_id, profile_options),
        exe_user_profile_update(user_id, project_id, profile_options),
        exe_user_profile_delete(user_id, project_id, profile_options),
    )
    if not all([p.ok() for p in ps]):
        return Promise.reject("Failed to add or update profiles")
    return Promise.resolve(None)


async def exe_user_profile_add(
    user_id: str, project_id: str, profile_options: MergeAddResult
) -> Promise[None]:
    if not len(profile_options["add"]):
        return Promise.resolve(None)
    LOG.info(f"Adding {len(profile_options['add'])} profiles for user {user_id}")
    task_add = await add_user_profiles(
        user_id,
        project_id,
        [ap["content"] for ap in profile_options["add"]],
        [ap["attributes"] for ap in profile_options["add"]],
    )
    return task_add


async def exe_user_profile_update(
    user_id: str, project_id: str, profile_options: MergeAddResult
) -> Promise[None]:
    if not len(profile_options["update"]):
        return Promise.resolve(None)
    LOG.info(f"Updating {len(profile_options['update'])} profiles for user {user_id}")
    task_update = await update_user_profiles(
        user_id,
        project_id,
        [up["profile_id"] for up in profile_options["update"]],
        [up["content"] for up in profile_options["update"]],
        [up["attributes"] for up in profile_options["update"]],
    )
    return task_update


async def exe_user_profile_delete(
    user_id: str, project_id: str, profile_options: MergeAddResult
) -> Promise[None]:
    if not len(profile_options["delete"]):
        return Promise.resolve(None)
    LOG.info(f"Deleting {len(profile_options['delete'])} profiles for user {user_id}")
    task_delete = await delete_user_profiles(
        user_id, project_id, profile_options["delete"]
    )
    return task_delete
