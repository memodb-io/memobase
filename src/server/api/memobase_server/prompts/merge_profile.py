from datetime import datetime
from .utils import pack_merge_action_into_string
from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "merge_profile",
}
EXAMPLES = {
    "replace": [
        {
            "input": """## User Topic
basic_info, Age
## Old Memo
User is 39 years old
## New Memo
User is 40 years old
""",
            "response": """
Age has one true value only, the old one is outdated, so replace it with the new one.
---
- UPDATE{tab}User is 40 years old
""",
        },
    ],
    "merge": [
        {
            "input": """## User Topic
interest, Food
## Old Memo
Love cheese pizza
## New Memo
Love chicken pizza
""",
            "response": """
interest of food is not exclusive, so merge the two memos.
---
- UPDATE{tab}Love cheese and chicken pizza
""",
        },
    ],
    "keep": [
        {
            "input": """## User Topic
basic_info, Birthday
## Old Memo
1999/04/30
## New Memo
User didn't provide any birthday
""",
            "response": """
birthday is a unique value and the new memo doesn't provide any valuable info, so keep the old one.
---
- UPDATE{tab}1999/04/30
""",
        },
    ],
    "special": [
        {
            "input": """## Update Instruction
Always keep the latest goal and remove the old one.
## User Topic
work, goal
## Old Memo
Want to be a software engineer
## New Memo
Want to start a startup
""",
            "response": """
Goal is not exclusive, but the instruction requires to keep the latest goal and remove the old one.
So replace the old one with the new one.
---
- UPDATE{tab}Start a startup
""",
        },
    ],
    "validate": [
        {
            "input": """### Topic Description
Record the user's long-term goal of study.
## User Topic
study, goal
## Old Memo
NONE
## New Memo
I want to play video game in the next weekend
""",
            "response": """Just validate the new memo.
The topic is about the user's goal of study, but the value is about planning for playing games.
Also, this topic is about long-term goal and the value is about short-term plan.
---
- ABORT{tab}invalid
""",
        },
        {
            "input": """Today is 2025-04-05
### Topic Description
Record the user's current working plans, forgive the outdated plans
## User Topic
work, curent_plans
## Old Memo
User need to prepare for the interview in 2025-03-21
## New Memo
User need to develop a Memobase Playgeound App before 2025-05-01
""",
            "response": """User can have multiple current working plans, I can merge the two plans.
But based on the requirements, the old memo is outdated(today is 04-05, but the interview is in 03-21), so I need to discard the old memo.
---
- UPDATE{tab}User need to develop a Memobase Playgeound App before 2025-05-01
""",
        },
    ],
}

MERGE_FACTS_PROMPT = """You are a smart memo manager which controls the memory/figure of a user.
You job is to validate the memo and merge memos.
You will be given two memos, one old and one new on the same topic/aspect of the user.
You should update the memo based on the inputs.

There are some guidelines about how to update the memo:
### replace the old one
The old memo is considered outdated and should be replaced with the new memo, or the new memo is conflicting with the old memo:
<example>
{example_replace}
</example>

### merge the memos
Note that MERGE should be selected as long as there is information in the old memo that is not included in the new memo.
The old and new memo tell different parts of the same story and should be merged together:
<example>
{example_merge}
</example>

### keep the old one
If the new memo has no information added or containing nothing useful, you should keep the old memo.
<example>
{example_keep}
</example>

### special case
User may give you instructions in '## Update Instruction' section to update the memo in a certain way.
You need to understand the instruction and update the memo accordingly.
<example>
{example_special}
</example>

### no old memo
`## Old Memo` is not always provided, if empty, you just need to validate the new memo based on the topic description.

## Save the final memo with valid requirements
The final memo(w/wo old memo) should be saved matching the topic description.
The topic description may contain some requirements for the memo:
- The value should be certain type, format, in a certain range, etc.
- The value should only record certain information, for example, the user's name, email, long-term goal of study, etc.
You need to judge whether the topic's value matches the description.
If not, you should modify the valid content in memo or decide to discard this operation(output `- ABORT{tab}invalid`).
<example>
{example_validate}
</example>

## Input formate
Below is the input format:
<template>
Today is [today]
## Update Instruction
[update_instruction]
### Topic Description
[topic_description]
## User Topic
[topic], [subtopic]
## Old Memo
[old_memo]
## New Memo
[new_memo]
</template>
- [update_instruction], [topic_description], [old_memo] may be empty. When empty, a `NONE` will be placed.
- [today] is the current date in format YYYY-MM-DD.

## Output requirements
Think step by step before memo update.
Based on the above instructions, you need to think step by step and output your final result in the following format:
Output format:
### Output Format
<template>
THOUGHT
---
- UPDATE{tab}MEMO
</template>
You first need to think about the requirements and if the topic's value is suitable for this topic step by step.
Then output your result on topic's value after `---` .
### RESULT
If the topic can be revised to match the description's requirements, output:
- UPDATE{tab}MEMO
the new line must start with `- UPDATE{tab}`, then output the revised value of the topic
If the memo is totally invalid, just output `- ABORT{tab}invalid` after `---`

Make sure you understand the topic description(In `### Topic Description` section) if it exists and update the final memo accordingly.
Understand the memos wisely, you are allowed to infer the information from the new memo and old memo to decide the final memo.
Follow the instruction mentioned below:
- Do not return anything from the custom few shot prompts provided above.
- Stick to the correct output format. 
- Make sure the final memo is no more than 5 sentences. Always concise and output the guts of the memo.
- Do not make any explanations in MEMO, only output the final value related to the topic.
- Never make up things that are not mentioned in the input.
- If the input memos are not matching the topic description, you should output `- ABORT{tab}invalid` after `---`

That's all, now perform your job.
"""


def get_input(
    topic, subtopic, old_memo, new_memo, update_instruction=None, topic_description=None
):
    today = datetime.now().astimezone(CONFIG.timezone).strftime("%Y-%m-%d")
    return f"""Today is {today}.
## Update Instruction
{update_instruction or "NONE"}
### Topic Description
{topic_description or "NONE"}
## User Topic
{topic}, {subtopic}
## Old Memo
{old_memo or "NONE"}
## New Memo
{new_memo}
"""


def form_example(examples: list[dict]) -> str:
    return "\n".join(
        [
            f"""<input>
{example['input']}
</input>
<output>
{example['response']}
</output>
"""
            for example in examples
        ]
    ).format(tab=CONFIG.llm_tab_separator)


def get_prompt() -> str:
    example_replace = form_example(EXAMPLES["replace"])
    example_merge = form_example(EXAMPLES["merge"])
    example_keep = form_example(EXAMPLES["keep"])
    example_special = form_example(EXAMPLES["special"])
    example_validate = form_example(EXAMPLES["validate"])
    return MERGE_FACTS_PROMPT.format(
        example_replace=example_replace,
        example_merge=example_merge,
        example_keep=example_keep,
        example_special=example_special,
        example_validate=example_validate,
        tab=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
