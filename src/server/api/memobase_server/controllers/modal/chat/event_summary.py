from typing import Optional
from ...project import get_project_profile_config
from ....models.utils import Promise
from ....models.blob import Blob, BlobType
from ....env import ProfileConfig, ContanstTable, CONFIG
from ....prompts.utils import tag_chat_blobs_in_order_xml, parse_string_into_subtopics
from ....prompts.types import read_out_event_tags, attribute_unify
from ....llms import llm_complete
from ....utils import get_encoded_tokens

from ....prompts import summary_chats as summary_chats_prompt
from ....prompts import event_tagging as event_tagging_prompt


async def summary_event(
    project_id: str,
    blobs: list[Blob],
    config: ProfileConfig,
) -> Promise[Optional[str]]:
    ENABLE_EVENT_SUMMARY = (
        config.enable_event_summary
        if config.enable_event_summary is not None
        else CONFIG.enable_event_summary
    )
    if not ENABLE_EVENT_SUMMARY:
        return Promise.resolve(None)
    chat_section = tag_chat_blobs_in_order_xml(blobs)
    if (
        len(get_encoded_tokens(chat_section))
        <= CONFIG.minimum_chats_token_size_for_event_summary
    ):
        return Promise.resolve(None)
    r = await llm_complete(
        project_id,
        chat_section,
        system_prompt=summary_chats_prompt.get_prompt(),
        temperature=0.2,
        model=CONFIG.summary_llm_model,
        **summary_chats_prompt.get_kwargs(),
    )
    return r


async def tag_event(
    project_id: str, config: ProfileConfig, profile_delta: str, event_summary: str
) -> Promise[Optional[list]]:
    event_tags = read_out_event_tags(config)
    available_event_tags = set([et.name for et in event_tags])
    if len(event_tags) == 0:
        return Promise.resolve(None)
    event_tags_str = "\n".join([f"- {et.name}({et.description})" for et in event_tags])
    r = await llm_complete(
        project_id,
        f"{profile_delta}\n\n{event_summary}",
        system_prompt=event_tagging_prompt.get_prompt(event_tags_str),
        temperature=0.2,
        model=CONFIG.best_llm_model,
        **event_tagging_prompt.get_kwargs(),
    )
    if not r.ok():
        return r
    parsed_event_tags = parse_string_into_subtopics(r.data())
    parsed_event_tags = [
        {"tag": attribute_unify(et["sub_topic"]), "value": et["memo"]}
        for et in parsed_event_tags
    ]
    print(f"{profile_delta}\n\n{event_summary}", event_tags_str, parsed_event_tags)
    strict_parsed_event_tags = [
        et for et in parsed_event_tags if et["tag"] in available_event_tags
    ]
    return Promise.resolve(strict_parsed_event_tags)
