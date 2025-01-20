import asyncio
from typing import TypedDict
import pydantic
from ....env import CONFIG, LOG
from ....utils import get_blob_str, get_encoded_tokens
from ....models.utils import Promise
from ....models.blob import Blob, BlobType
from ....models.response import ProfileData, AIUserProfiles, CODE
from ....llms import llm_complete
from ....prompts import (
    extract_profile,
    merge_profile,
    summary_profile,
    zh_extract_profile,
    zh_merge_profile,
)
from ....prompts.utils import (
    tag_chat_blobs_in_order_xml,
    attribute_unify,
    parse_string_into_profiles,
    parse_string_into_merge_action,
)
from ...profile import get_user_profiles, update_user_profile, add_user_profiles
from .types import UpdateProfile, AddProfile


async def re_summary(
    add_profile: list[AddProfile],
    update_profile: list[UpdateProfile],
):
    add_tasks = [summary_memo(ap) for ap in add_profile]
    await asyncio.gather(*add_tasks)
    update_tasks = [summary_memo(up) for up in update_profile]
    await asyncio.gather(*update_tasks)


async def summary_memo(content_pack: dict) -> None:
    content = content_pack["content"]
    if len(get_encoded_tokens(content)) <= CONFIG.max_pre_profile_token_size:
        return
    r = await llm_complete(
        content_pack["content"],
        system_prompt=summary_profile.get_prompt(),
        temperature=0.2,  # precise
    )
    if not r.ok():
        LOG.error(f"Failed to summary memo: {r.msg()}")
        return
    content_pack["content"] = r.data()
