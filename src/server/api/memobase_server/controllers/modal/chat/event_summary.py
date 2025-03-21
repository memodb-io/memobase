from typing import Optional
from ...project import get_project_profile_config
from ....models.utils import Promise
from ....models.blob import Blob, BlobType
from ....env import ProfileConfig, ContanstTable, CONFIG
from ....prompts import summary_chats as summary_chats_prompt
from ....prompts.utils import tag_chat_blobs_in_order_xml
from ....llms import llm_complete


async def summary_event(
    project_id: str,
    blobs: list[Blob],
    config: ProfileConfig,
) -> Promise[Optional[dict]]:
    ENABLE_EVENT_SUMMARY = (
        config.enable_event_summary
        if config.enable_event_summary is not None
        else CONFIG.enable_event_summary
    )
    if not ENABLE_EVENT_SUMMARY:
        return Promise.resolve(None)
    r = await llm_complete(
        project_id,
        tag_chat_blobs_in_order_xml(blobs),
        system_prompt=summary_chats_prompt.get_prompt(),
        temperature=0.2,
        **summary_chats_prompt.get_kwargs(),
    )
    return r
