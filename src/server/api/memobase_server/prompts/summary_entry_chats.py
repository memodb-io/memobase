from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "summary_entry_chats",
}
SUMMARY_PROMPT = """You are a expert of logging personal info, schedule, events from chats.
You will be given a chats between a user and an assistant.

## Requirement
- You need to list all possible user info
- You need to list all possible schedule
- If the user event/schedule has specific mention time or event happen time. Convert the event date info in the message based on [TIME] after your log. for example
    Input: `[2024/04/30] user: I bought a new car yesterday!`
    Output: `user bought a new car. [mention 2024/04/30, buy car in 2024/04/29]`
    Input: `[2024/04/30] user: I bought a car 4 years ago!`
    Output: `user bought a car. [mention 2024/04/30, buy car in 2020]`
    Explain: because you don't know the exact date, only year, so 2024-4=2020. or you can log at [4 years before 2024/04/30]
    Input: `[2024/04/30] user: I bought a new car last week!`
    Output: `user bought a new car. [mention 2024/04/30, buy car in 2024/04/30 a week before]`
    Explain: because you don't know the exact date.
    Input: `[...] user: I bought a new car last week!`
    Output: `user bought a new car.`
    Explain: because you don't know the exact date, so don't attach any date.

## Special Requirements
Below is the special requirements for your job:
{additional_requirements}
If empty, just ignore it. Otherwise, you must follow those requirements.

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
- LOGGING[TIME INFO] // TYPE
Output your logging result in Markdown unorder list format.
For example:
```
- Jack paint a picture about his kids.[mention 2023/1/23] // event
- User's alias is Jack, assistant is Melinda. // info
- Jack mentioned his work is software engineer in Memobase. [mention 2023/1/23] // info
- Jack plans to go the gym. [mention 2023/1/23, plan in 2023/1/24] // schedule
...
```
Always add specific mention time of your log, and the event happen time if possible.
Remember, make sure your logging is pure and concise, any time info should move to [TIME INFO] block.

Finally, The logging result should use the same language as the chats. English in, English out. Chinese in, Chinese out.
Now perform your task.
"""


def pack_input(chat_strs):
    return f"""#### Chats
{chat_strs}
"""


def get_prompt(
    topic_examples: str, attribute_examples: str, additional_requirements: str = ""
) -> str:
    return SUMMARY_PROMPT.format(
        topics=topic_examples,
        attributes=attribute_examples,
        additional_requirements=additional_requirements,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
