from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "summary_chats",
}
SUMMARY_PROMPT = """You are a expert of summarizing chats.
You will be given a chats between a user and an assistant.

## Requirement
- Your task is to summarize the chats into 1~2 sentences.
- Only extract the most critical events/schedules that occurred.
- Specific Time(YYYY/MM/DD) should be included in events/schedules if possible.
- Only return the plain summary and no explanation.

The summary should use the same language as the chats.
"""


def get_prompt() -> str:
    return SUMMARY_PROMPT


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
