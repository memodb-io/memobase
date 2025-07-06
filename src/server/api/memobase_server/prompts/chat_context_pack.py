from typing import Callable

ContextPromptFunc = Callable[[str, str], str]


def en_context_prompt(profile_section: str, event_section: str) -> str:
    return f"""---
# Memory
Unless the user has relevant queries, do not actively mention those memories in the conversation.
## User Current Profile:
{profile_section}

## Past Events:
{event_section}
---
"""


def zh_context_prompt(profile_section: str, event_section: str) -> str:
    return f"""---
# 记忆
除非用户有相关的需求，否则不要主动在对话中提到这些记忆.
## 用户当前状态：
{profile_section}

## 过去事件：
{event_section}
---
"""


CONTEXT_PROMPT_PACK: dict[str, ContextPromptFunc] = {
    "en": en_context_prompt,
    "zh": zh_context_prompt,
}
