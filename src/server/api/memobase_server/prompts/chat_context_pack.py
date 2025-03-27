from typing import Callable

ContextPromptFunc = Callable[[str, str], str]


def en_context_prompt(profile_section: str, event_section: str) -> str:
    return f"""<memory>
# Below is the user profile:
{profile_section}

# Below is the latest events of the user:
{event_section}
</memory>
Please provide your answer using the information within the <memory> tag at the appropriate time.
"""


def zh_context_prompt(profile_section: str, event_section: str) -> str:
    return f"""<memory>
# 以下是用户的用户画像：
{profile_section}

# 以下是用户的最近事件：
{event_section}
</memory>
请在适当的时候使用<memory>标签中的信息。
"""


CONTEXT_PROMPT_PACK: dict[str, ContextPromptFunc] = {
    "en": en_context_prompt,
    "zh": zh_context_prompt,
}
