import asyncio
from ....env import CONFIG
from ....models.utils import Promise
from ....models.blob import Blob, BlobType
from ....llms import llm_complete
from ....prompts.profile_init_utils import read_out_profile_config
from ...project import ProfileConfig
from ....prompts.profile_init_utils import read_out_event_tags
from ....prompts.utils import tag_chat_blobs_in_order_xml
from .types import FactResponse, PROMPTS


async def entry_chat_summary(
    user_id: str, project_id: str, blobs: list[Blob], project_profiles: ProfileConfig
) -> Promise[str]:
    assert all(b.type == BlobType.chat for b in blobs), "All blobs must be chat blobs"
    USE_LANGUAGE = project_profiles.language or CONFIG.language
    project_profiles_slots = read_out_profile_config(
        project_profiles, PROMPTS[USE_LANGUAGE]["profile"].CANDIDATE_PROFILE_TOPICS
    )
    prompt = PROMPTS[USE_LANGUAGE]["entry_summary"]
    event_summary_theme = (
        project_profiles.event_theme_requirement or CONFIG.event_theme_requirement
    )

    event_tags = read_out_event_tags(project_profiles)
    event_attriubtes_str = "\n".join(
        [f"- {et.name}({et.description})" for et in event_tags]
    )
    profile_topics_str = PROMPTS[USE_LANGUAGE]["profile"].get_prompt(
        project_profiles_slots
    )
    blob_strs = tag_chat_blobs_in_order_xml(blobs)
    r = await llm_complete(
        project_id,
        prompt.pack_input(blob_strs),
        system_prompt=prompt.get_prompt(
            profile_topics_str,
            event_attriubtes_str,
            additional_requirements=event_summary_theme,
        ),
        temperature=0.2,  # precise
        model=CONFIG.summary_llm_model,
        **prompt.get_kwargs(),
    )
    return r
