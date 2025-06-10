from ...project import get_project_profile_config
from ....connectors import Session
from ....env import LOG, ProfileConfig, CONFIG
from ....utils import get_blob_str, get_encoded_tokens
from ....models.blob import Blob
from ....models.utils import Promise, CODE
from ....models.response import IdsData, ChatModalResponse
from ...profile import add_update_delete_user_profiles
from ...event import append_user_event
from .extract import extract_topics
from .merge import merge_or_valid_new_memos
from .summary import re_summary
from .organize import organize_profiles
from .types import MergeAddResult
from .event_summary import tag_event
from .entry_summary import entry_chat_summary


def truncate_chat_blobs(
    blobs: list[Blob], max_token_size: int
) -> tuple[list[str], list[Blob]]:
    results = []
    total_token_size = 0
    for b in blobs[::-1]:
        ts = len(get_encoded_tokens(get_blob_str(b)))
        total_token_size += ts
        if total_token_size <= max_token_size:
            results.append(b)
        else:
            break
    return results[::-1]


async def process_blobs(
    user_id: str, project_id: str, blobs: list[Blob]
) -> Promise[ChatModalResponse]:
    # 1. Extract patch profiles
    blobs = truncate_chat_blobs(blobs, CONFIG.max_chat_blob_buffer_process_token_size)
    if len(blobs) == 0:
        return Promise.reject(
            CODE.SERVER_PARSE_ERROR, "No blobs to process after truncating"
        )

    p = await get_project_profile_config(project_id)
    if not p.ok():
        return p
    project_profiles = p.data()

    p = await entry_chat_summary(user_id, project_id, blobs, project_profiles)
    if not p.ok():
        return p
    user_memo_str = p.data()

    p = await extract_topics(user_id, project_id, user_memo_str, project_profiles)
    if not p.ok():
        return p
    extracted_data = p.data()

    # 2. Merge it to thw whole profile
    p = await merge_or_valid_new_memos(
        project_id,
        fact_contents=extracted_data["fact_contents"],
        fact_attributes=extracted_data["fact_attributes"],
        profiles=extracted_data["profiles"],
        config=project_profiles,
        total_profiles=extracted_data["total_profiles"],
    )
    if not p.ok():
        return p

    profile_options = p.data()
    delta_profile_data = [
        p for p in (profile_options["add"] + profile_options["update_delta"])
    ]

    # 3. Check if we need to organize profiles
    p = await organize_profiles(
        project_id,
        profile_options,
        config=project_profiles,
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

    # FIXME using one session for all operations
    p = await handle_session_event(
        user_id,
        project_id,
        user_memo_str,
        delta_profile_data,
        project_profiles,
    )
    if not p.ok():
        return p
    eid = p.data()

    p = await handle_user_profile_db(user_id, project_id, profile_options)
    if not p.ok():
        return p
    return Promise.resolve(
        ChatModalResponse(
            event_id=eid,
            add_profiles=p.data().ids,
            update_profiles=[up["profile_id"] for up in profile_options["update"]],
            delete_profiles=profile_options["delete"],
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


async def handle_user_profile_db(
    user_id: str, project_id: str, profile_options: MergeAddResult
) -> Promise[IdsData]:
    LOG.info(f"Adding {len(profile_options['add'])} profiles for user {user_id}")
    LOG.info(f"Updating {len(profile_options['update'])} profiles for user {user_id}")
    LOG.info(f"Deleting {len(profile_options['delete'])} profiles for user {user_id}")

    p = await add_update_delete_user_profiles(
        user_id,
        project_id,
        [ap["content"] for ap in profile_options["add"]],
        [ap["attributes"] for ap in profile_options["add"]],
        [up["profile_id"] for up in profile_options["update"]],
        [up["content"] for up in profile_options["update"]],
        [up["attributes"] for up in profile_options["update"]],
        profile_options["delete"],
    )
    return p
