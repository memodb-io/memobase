from ..models.utils import Promise
from ..models.response import ContextData
from ..prompts.chat_context_pack import CONTEXT_PROMPT_PACK
from ..utils import get_encoded_tokens, event_str_repr
from ..env import CONFIG
from .project import get_project_profile_config
from .profile import get_user_profiles, truncate_profiles
from .event import get_user_events


async def get_user_context(
    user_id: str,
    project_id: str,
    max_token_size: int,
    prefer_topics: list[str],
    only_topics: list[str],
    max_subtopic_size: int,
    topic_limits: dict[str, int],
    profile_event_ratio: float,
    require_event_summary: bool,
) -> Promise[ContextData]:
    assert 0 < profile_event_ratio <= 1, "profile_event_ratio must be between 0 and 1"
    max_profile_token_size = int(max_token_size * profile_event_ratio)
    max_event_token_size = max_token_size - max_profile_token_size

    p = await get_project_profile_config(project_id)
    if not p.ok():
        return p
    profile_config = p.data()
    use_language = profile_config.language or CONFIG.language
    context_prompt_func = CONTEXT_PROMPT_PACK[use_language]

    p = await get_user_profiles(user_id, project_id)
    if not p.ok():
        return p
    if max_profile_token_size > 0:
        user_profiles = p.data()
        use_profiles = await truncate_profiles(
            user_profiles,
            prefer_topics=prefer_topics,
            only_topics=only_topics,
            max_token_size=max_profile_token_size,
            max_subtopic_size=max_subtopic_size,
            topic_limits=topic_limits,
        )
        if not use_profiles.ok():
            return use_profiles
        use_profiles = use_profiles.data().profiles

        profile_section = "- " + "\n- ".join(
            [
                f"{p.attributes.get('topic')}::{p.attributes.get('sub_topic')}: {p.content}"
                for p in use_profiles
            ]
        )
    else:
        profile_section = ""

    profile_section_tokens = len(get_encoded_tokens(profile_section))
    max_event_token_size = min(
        max_token_size - profile_section_tokens, max_event_token_size
    )
    if max_event_token_size <= 0:
        return Promise.resolve(
            ContextData(context=context_prompt_func(profile_section, ""))
        )

    # max 40 events, then truncate to max_event_token_size
    p = await get_user_events(
        user_id,
        project_id,
        topk=40,
        max_token_size=max_event_token_size,
        need_summary=require_event_summary,
    )
    if not p.ok():
        return p
    user_events = p.data()
    event_section = "\n---\n".join([event_str_repr(ed) for ed in user_events.events])

    return Promise.resolve(
        ContextData(context=context_prompt_func(profile_section, event_section))
    )
