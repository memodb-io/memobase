from functools import partial
from ..models.utils import Promise, CODE
from ..models.response import ContextData, OpenAICompatibleMessage, UserEventGistsData
from ..prompts.chat_context_pack import CONTEXT_PROMPT_PACK
from ..utils import get_encoded_tokens
from ..env import CONFIG, TRACE_LOG
from .project import get_project_profile_config
from .profile import get_user_profiles, truncate_profiles
from .post_process.profile import filter_profiles_with_chats

# from .event import get_user_events, search_user_events, truncate_events
from .event_gist import (
    get_user_event_gists,
    truncate_event_gists,
    search_user_event_gists,
)


def customize_context_prompt_func(
    context_prompt: str, profile_section: str, event_section: str
) -> str:
    return context_prompt.format(
        profile_section=profile_section, event_section=event_section
    )


def pack_latest_chat(chats: list[OpenAICompatibleMessage], chat_num: int = 3) -> str:
    return "\n".join([f"{m.content}" for m in chats[-chat_num:]])


async def get_user_profiles_data(
    user_id: str,
    project_id: str,
    max_profile_token_size: int,
    prefer_topics: list[str],
    only_topics: list[str],
    max_subtopic_size: int,
    topic_limits: dict[str, int],
    chats: list[OpenAICompatibleMessage],
    full_profile_and_only_search_event: bool,
) -> Promise[tuple[str, list]]:
    """Retrieve and process user profiles."""
    p = await get_user_profiles(user_id, project_id)
    if not p.ok():
        return p
    total_profiles = p.data()

    if max_profile_token_size > 0:
        if chats and (not full_profile_and_only_search_event):
            p = await filter_profiles_with_chats(
                user_id,
                project_id,
                total_profiles,
                chats,
                only_topics=only_topics,
            )
            if p.ok():
                total_profiles.profiles = p.data()["profiles"]

        user_profiles = total_profiles
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
        use_profiles = []

    return Promise.resolve((profile_section, use_profiles))


async def get_user_event_gists_data(
    user_id: str,
    project_id: str,
    chats: list[OpenAICompatibleMessage],
    require_event_summary: bool,
    event_similarity_threshold: float,
    time_range_in_days: int,
) -> Promise[UserEventGistsData]:
    """Retrieve user events data."""
    if chats and CONFIG.enable_event_embedding:
        search_query = pack_latest_chat(chats)
        p = await search_user_event_gists(
            user_id,
            project_id,
            query=search_query,
            topk=60,
            similarity_threshold=event_similarity_threshold,
            time_range_in_days=time_range_in_days,
        )
    else:
        p = await get_user_event_gists(
            user_id,
            project_id,
            topk=60,
            time_range_in_days=time_range_in_days,
        )
    return p


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
    chats: list[OpenAICompatibleMessage],
    event_similarity_threshold: float,
    time_range_in_days: int,
    customize_context_prompt: str = None,
    full_profile_and_only_search_event: bool = False,
    fill_window_with_events: bool = False,
) -> Promise[ContextData]:
    import asyncio

    assert 0 < profile_event_ratio <= 1, "profile_event_ratio must be between 0 and 1"
    max_profile_token_size = int(max_token_size * profile_event_ratio)

    p = await get_project_profile_config(project_id)
    if not p.ok():
        return p
    profile_config = p.data()
    use_language = profile_config.language or CONFIG.language
    context_prompt_func = CONTEXT_PROMPT_PACK[use_language]
    if customize_context_prompt is not None:
        context_prompt_func = partial(
            customize_context_prompt_func, customize_context_prompt
        )

    # Execute profile and event retrieval in parallel
    profile_result, event_gist_result = await asyncio.gather(
        get_user_profiles_data(
            user_id,
            project_id,
            max_profile_token_size,
            prefer_topics,
            only_topics,
            max_subtopic_size,
            topic_limits,
            chats,
            full_profile_and_only_search_event,
        ),
        get_user_event_gists_data(
            user_id,
            project_id,
            chats,
            require_event_summary,
            event_similarity_threshold,
            time_range_in_days,
        ),
        return_exceptions=True,
    )

    # Handle profile result
    if isinstance(profile_result, Exception):
        return Promise.reject(
            CODE.SERVER_PARSE_ERROR, f"Profile retrieval failed: {str(profile_result)}"
        )
    if not profile_result.ok():
        return profile_result
    profile_section, use_profiles = profile_result.data()

    # Handle event result
    if isinstance(event_gist_result, Exception):
        return Promise.reject(
            CODE.SERVER_PARSE_ERROR, f"Event retrieval failed: {str(event_gist_result)}"
        )
    if not event_gist_result.ok():
        return event_gist_result
    user_event_gists = event_gist_result.data()

    # Calculate token sizes and truncate events if needed
    profile_section_tokens = len(get_encoded_tokens(profile_section))
    if fill_window_with_events:
        max_event_token_size = max_token_size - profile_section_tokens
    else:
        max_event_token_size = min(
            max_token_size - profile_section_tokens,
            max_token_size - max_profile_token_size,
        )

    if max_event_token_size <= 0:
        return Promise.resolve(
            ContextData(context=context_prompt_func(profile_section, ""))
        )

    # Truncate events based on calculated token size
    p = await truncate_event_gists(user_event_gists, max_event_token_size)
    if not p.ok():
        return p
    user_event_gists = p.data()

    event_section = "\n".join([ed.gist_data.content for ed in user_event_gists.gists])
    event_section_tokens = len(get_encoded_tokens(event_section))

    TRACE_LOG.info(
        project_id,
        user_id,
        f"Retrieved {len(use_profiles)} profiles({profile_section_tokens} tokens), {len(user_event_gists.gists)} event gists({event_section_tokens} tokens)",
    )

    return Promise.resolve(
        ContextData(context=context_prompt_func(profile_section, event_section))
    )
