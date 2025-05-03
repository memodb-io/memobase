import asyncio

from ....env import LOG, ProfileConfig
from ....models.blob import Blob
from ....models.utils import Promise
from ....models.response import IdsData, ChatModalResponse
from ...profile import add_user_profiles, update_user_profiles, delete_user_profiles
from ...event import append_user_event
from .extract import extract_topics
from .merge import merge_or_valid_new_memos
from .summary import re_summary
from .organize import organize_profiles
from .types import MergeAddResult
from .event_summary import tag_event
from .entry_summary import entry_summary


async def process_blobs(
    user_id: str, project_id: str, blob_ids: list[str], blobs: list[Blob]
) -> Promise[ChatModalResponse]:
    # 1. Extract patch profiles
    p = await entry_summary(user_id, project_id, blobs)
    if not p.ok():
        return p
    user_memo_str = p.data()

    p = await extract_topics(user_id, project_id, user_memo_str)
    if not p.ok():
        return p
    extracted_data = p.data()

    # 2. Merge it to thw whole profile
    p = await merge_or_valid_new_memos(
        project_id,
        fact_contents=extracted_data["fact_contents"],
        fact_attributes=extracted_data["fact_attributes"],
        profiles=extracted_data["profiles"],
        config=extracted_data["config"],
        total_profiles=extracted_data["total_profiles"],
    )
    if not p.ok():
        return p

    profile_options = p.data()
    delta_profile_data = [
        p for p in (profile_options["add"] + profile_options["update_delta"])
    ]
    p = await handle_session_event(
        user_id,
        project_id,
        user_memo_str,
        delta_profile_data,
        extracted_data["config"],
    )
    if not p.ok():
        return p
    eid = p.data()

    # 3. Check if we need to organize profiles
    p = await organize_profiles(
        project_id,
        profile_options,
        config=extracted_data["config"],
    )
    if not p.ok():
        LOG.error(f"Failed to organize profiles: {p.msg()}")

    # 4. Re-summary profiles if any slot is too big
    p = await re_summary(
        project_id,
        add_profile=profile_options["add"],
        update_profile=profile_options["update"],
    )
    if not p.ok():
        LOG.error(f"Failed to re-summary profiles: {p.msg()}")

    # DB commit
    p = await exe_user_profile_add(user_id, project_id, profile_options)
    if not p.ok():
        return p
    add_profile_ids = p.data().ids
    p = await exe_user_profile_update(user_id, project_id, profile_options)
    if not p.ok():
        return p
    update_profile_ids = p.data().ids
    p = await exe_user_profile_delete(user_id, project_id, profile_options)
    if not p.ok():
        return p
    delete_profile_ids = p.data().ids
    return Promise.resolve(
        ChatModalResponse(
            event_id=eid,
            add_profiles=add_profile_ids,
            update_profiles=update_profile_ids,
            delete_profiles=delete_profile_ids,
        )
    )


async def handle_session_event(
    user_id: str,
    project_id: str,
    memo_str: str,
    delta_profile_data: list[dict],
    config: ProfileConfig,
) -> Promise[str]:
    if not len(delta_profile_data):
        return Promise.resolve(None)
    event_tip = memo_str
    p = await tag_event(project_id, config, event_tip)
    if not p.ok():
        LOG.error(f"Failed to tag event: {p.msg()}")
    event_tags = p.data() if p.ok() else None

    eid = await append_user_event(
        user_id,
        project_id,
        {
            "event_tip": event_tip,
            "event_tags": event_tags,
            "profile_delta": delta_profile_data,
        },
    )

    return eid


async def exe_user_profile_add(
    user_id: str, project_id: str, profile_options: MergeAddResult
) -> Promise[IdsData]:
    if not len(profile_options["add"]):
        return Promise.resolve(IdsData(ids=[]))
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
) -> Promise[IdsData]:
    if not len(profile_options["update"]):
        return Promise.resolve(IdsData(ids=[]))
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
        return Promise.resolve(IdsData(ids=[]))
    LOG.info(f"Deleting {len(profile_options['delete'])} profiles for user {user_id}")
    task_delete = await delete_user_profiles(
        user_id, project_id, profile_options["delete"]
    )
    return task_delete
