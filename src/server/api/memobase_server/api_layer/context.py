import json

from ..controllers import full as controllers

from ..models.response import CODE, UUID
from ..models.utils import Promise
from ..models import response as res
from fastapi import Request
from fastapi import Path, Query


async def get_user_context(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    max_token_size: int = Query(
        1000,
        description="Max token size of returned Context",
    ),
    prefer_topics: list[str] = Query(
        None,
        description="Rank prefer topics at first to try to keep them in filtering, default order is by updated time",
    ),
    only_topics: list[str] = Query(
        None,
        description="Only return profiles with these topics, default is all",
    ),
    max_subtopic_size: int = Query(
        None,
        description="Max subtopic size of the same topic in returned Context",
    ),
    topic_limits_json: str = Query(
        None,
        description='Set specific subtopic limits for topics in JSON, for example {"topic1": 3, "topic2": 5}. The limits in this param will override `max_subtopic_size`.',
    ),
    profile_event_ratio: float = Query(
        0.6,
        description="Profile event ratio of returned Context",
    ),
    require_event_summary: bool = Query(
        False,
        description="Whether to require event summary in returned Context",
    ),
    chats_str: str = Query(
        None,
        description="""Pass the recent chats to enable context search. 
Memobase will use those chats to search for relevant events.
It's a list of chats in OpenAI Message format, for example: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}].

**NOTICE**
- It will increase your latency by 0.1-1 seconds, because Memobase will use Embedding to search for relevant profiles and events.
- It will cost your Memobase tokens, roughly 100~200 tokens per chat based on the profile size.
- The profiles in the context will not be searched by the `chats_str`.
- If you want also search profiles, see `full_profile_and_only_search_event` query parameter.
""",
    ),
    event_similarity_threshold: float = Query(
        0.2,
        description="Event similarity threshold of returned Context",
    ),
    time_range_in_days: int = Query(
        180,
        description="Only allow events within the past few days, default is 180",
    ),
    customize_context_prompt: str = Query(
        None,
        description="""Customize context prompt template.
- use `{profile_section}` to refer to the profile section
- use `{event_section}` to refer to the event section

For example:
```
# Memory
Unless the user has relevant queries, do not actively mention those memories in the conversation.
## User Background:
{profile_section}

## Latest Events:
{event_section}
```
""",
    ),
    full_profile_and_only_search_event: bool = Query(
        True,
        description="""If you pass `chats_str` and set this to `False`, Memobase will search for relevant profiles and events at the same time.
**NOTICE**
- It will increase your latency by 2-5(based on the profile size) seconds, because Memobase will use LLM and Embedding to search for relevant profiles and events.
- It will cost your Memobase tokens, roughly 100~1000 tokens per chat based on the profile size.
""",
    ),
    fill_window_with_events: bool = Query(
        False,
        description="If set to `True`, Memobase will fill the token window with the rest events.",
    ),
) -> res.UserContextDataResponse:
    project_id = request.state.memobase_project_id
    topic_limits_json = topic_limits_json or "{}"
    chats_str = chats_str or "[]"
    try:
        topic_limits = res.StrIntData(data=json.loads(topic_limits_json)).data
        chats = res.MessageData(data=json.loads(chats_str)).data
    except Exception as e:
        return Promise.reject(CODE.BAD_REQUEST, f"Invalid JSON: {e}").to_response(
            res.UserContextDataResponse
        )
    p = await controllers.context.get_user_context(
        user_id,
        project_id,
        max_token_size,
        prefer_topics,
        only_topics,
        max_subtopic_size,
        topic_limits,
        profile_event_ratio,
        require_event_summary,
        chats,
        event_similarity_threshold,
        time_range_in_days,
        customize_context_prompt=customize_context_prompt,
        full_profile_and_only_search_event=full_profile_and_only_search_event,
        fill_window_with_events=fill_window_with_events,
    )
    return p.to_response(res.UserContextDataResponse)
