from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "summary_entry_chats",
}
SUMMARY_PROMPT = """You are a expert of logging personal info, schedule, events from chats.
You will be given a chats between a user and an assistant.

## Requirement
- You need to list all possible user info
- You need to list all possible schedule
- You need to list the user events with detailed datetime. Convert the event date info in the message based on [TIME] after your log. for example
    Input: `[2024/04/30] user: I bought a new car yesterday!`
    Output: `user bought a new car. [mention 2024/04/29, happen at 2024/04/30]`
    Input: `[2024/04/30] user: I bought a car 4 years ago!`
    Output: `user bought a car. [mention 2024/04/30, happen at 2020]`
    Explain: because you don't know the exact date, only year, so 2024-4=2020. or you can log at [4 years before 2024/04/30]
    Input: `[2024/04/30] user: I bought a new car last week!`
    Output: `user bought a new car. [mention 2024/04/30, happen at a week before 2024/04/30]`
    Explain: because you don't know the exact date.

### Important Info
Below is the topics/subtopics you should log from the chats.
<topics>
{topics}
</topics>
Below is the important attributes you should log from the chats.
<attributes>
{attributes}
</attributes>

#### Input Chats
You will receive a conversation between the user and the assistant. The format of the conversation is:
- [TIME] NAME: MESSAGE
where NAME is ALIAS(ROLE) or just ROLE, when ALIAS is available, use ALIAS to refer user/assistant.
MESSAGE is the content of the conversation.
TIME is the time of this message happened, so you need to convert the date info in the message based on TIME if necessary.

## Output Format
Output your logging result in Markdown unorder list format.
For example:
```
## Events
- Jack paint a picture about his kids today.[mention 2023/1/23]
## User Info
- User mentioned his work is software engineer in Memobase. [mention 2023/1/23]
## Schedules
- User plans to go the gym tomorrow. [mention 2023/1/23, happen at 2023/1/24]
...
```
Always add specific mention time of your log, and the event happen time if possible.

Finally, The logging result should use the same language as the chats. English in, English out. Chinese in, Chinese out.
Now perform your task.
"""


def pack_input(chat_strs):
    return f"""#### Chats
{chat_strs}
"""


def get_prompt(topic_examples: str, attribute_examples: str) -> str:
    return SUMMARY_PROMPT.format(topics=topic_examples, attributes=attribute_examples)


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
