from ..env import CONFIG
from datetime import datetime

ADD_KWARGS = {
    "prompt_id": "validate_profile",
}
EXAMPLES = [
    {
        "input": """### Topic Description
Record the user's long-term goal of study.

## User Topic
study, goal

## Value
I want to play video game in the next weekend""",
        "response": """The topic is about the user's goal of study, but the value is about planning for playing games.
Also, this topic is about long-term goal and the value is about short-term plan.
---
NONE""",
    },
    {
        "input": """### Topic Description
Start date of User's current work, in format YYYY-MM-DD

## User Topic
work, start_date

## Value
User started his work on 2024-01-01""",
        "response": """The format of the value is not precise.
---
- SAVE{tab}2024-01-01""",
    },
    {
        "input": """### Topic Description
用户的长期工作目标，整理成[目标]-[时间]的格式

## User Topic
工作, 目标

## Value
2024年6月份，用户需要完成一个项目，项目的目标是开发一个在线的AI助手""",
        "response": """值符合描述，但是需要重新整理下格式
---
- SAVE{tab}[开发一个在线的AI助手]-[2024-06]""",
    },
]

VALIDATE_FACTS_PROMPT = """You need to validate whether a topic's value matches the description.

## Examples
{examples}

## Input
You will be given the topic, the descrption of a topic, and the value of this topic.
You need to read out the description, especially the requirements of the topic's value, for example:
- The value should be certain type, format, in a certain range, etc.
- The value should only record certain information, for example, the user's name, email, long-term goal of study, etc.
You need to judge whether the topic's value matches the description.

## Output
Output the revised topic's value if it's not totally invalid, otherwise just return 'NONE'
### Output Format
```
THOUGHT
---
RESULT
```
You first need to think about the requirements and if the topic's value is suitable for this topic step by step.
Then output your result on topic's value after `---` .
### RESULT
If the topic can be revised to match the description's requirements, output:
- SAVE{tab}SAVED_VALUE
the new line must start with `- SAVE{tab}`, then output the revised value of the topic
If the topic is totally invalid, just output `NONE`

!!! Your should only decide to remove this topic or save (some of) it. You should never make up things that are not mentioned in the input.
!!! Never add your explanation to on SAVED_VALUE, just output the final value after your thought or just output `NONE` to reject this topic.s
That's all.
Now, follow the instructions to validate the topic.
"""


def get_input(topic, subtopic, new_memo, topic_description):
    today = datetime.now().astimezone(CONFIG.timezone).strftime("%Y-%m-%d")
    topic_section = f"""Today is {today}.
## User Topic
{topic}, {subtopic}
### Topic Description
{topic_description}"""

    return f"""{topic_section}
## Value
{new_memo}
"""


def get_prompt() -> str:
    examples = "\n".join(
        [
            f"""<example id={i}>
<input>
{example["input"]}
</input>
<output>
{example["response"]}
</output>
</example>"""
            for i, example in enumerate(EXAMPLES)
        ]
    )
    return VALIDATE_FACTS_PROMPT.format(
        examples=examples.format(tab=CONFIG.llm_tab_separator),
        tab=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
