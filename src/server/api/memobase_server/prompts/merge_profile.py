from datetime import datetime
from .utils import pack_merge_action_into_string
from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "merge_profile",
}
EXAMPLES = [
    {
        "input": """## User Topic
basic_info, Age

## Old Memo
User is 39 years old
## New Memo
User is 40 years old
""",
        "response": {
            "action": "UPDATE",
            "memo": "User is 40 years old",
        },
    },
    {
        "input": """## User Topic
interest, Food

## Old Memo
Love cheese pizza
## New Memo
Love chicken pizza
""",
        "response": {
            "action": "UPDATE",
            "memo": "Love cheese and chicken pizza",
        },
    },
    {
        "input": """## User Topic
basic_info, Birthday

## Old Memo
1999/04/30
## New Memo
User didn't provide any birthday
""",
        "response": {
            "action": "UPDATE",
            "memo": "1999/04/30",
        },
    },
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
        "response": {
            "action": "UPDATE",
            "memo": "Start a startup",
        },
    },
]

MERGE_FACTS_PROMPT = """You are a smart memo manager which controls the memory/figure of a user.
You will be given two memos, one old and one new on the same topic/aspect of the user.
You should update the old memo with the new memo.
And return your results in output format:
- UPDATE{tab}MEMO
start with '- ' and following is 'UPDATE', '{tab}' and then the final MEMO.

There are some guidelines about how to update the memo:
## replace the old one
The old memo is considered outdated and should be replaced with the new memo, or the new memo is conflicting with the old memo:
<example>
{example_replace}
</example>

## merge the memos
Note that MERGE should be selected as long as there is information in the old memo that is not included in the new memo.
The old and new memo tell different parts of the same story and should be merged together:
<example>
{example_merge}
</example>

## keep the old one
If the new memo has no information added or containing nothing useful, you should keep the old memo.
<example>
{example_keep}
</example>

## special case
User may give you instructions in '## Update Instruction' section to update the memo in a certain way.
You need to understand the instruction and update the memo accordingly.
<example>
{example_special}
</example>

Make sure you understand the topic description(In `### Topic Description` section) if it exists and update the final memo accordingly.
Understand the memos wisely, you are allowed to infer the information from the new memo and old memo to decide the final memo.
Follow the instruction mentioned below:
- Do not return anything from the custom few shot prompts provided above.
- Stick to the correct format.
- Make sure the final memo is no more than 5 sentences.
- Always concise and output the guts of the memo.
- Do not make any explanations in the memo, only output the final value related to the topic.
"""


def get_input(
    topic, subtopic, old_memo, new_memo, update_instruction=None, topic_description=None
):
    today = datetime.now().astimezone(CONFIG.timezone).strftime("%Y-%m-%d")
    header = ""
    if update_instruction:
        header = f"""## Update Instruction
{update_instruction}"""
    topic_section = f"""## User Topic
{topic}, {subtopic}"""
    if topic_description:
        topic_section += f"""
### Topic Description
{topic_description}"""

    return f"""Today is {today}.
{header}
{topic_section}

## Old Memo
{old_memo}
## New Memo
{new_memo}
"""


def get_prompt() -> str:
    example_replace = f"""INPUT:
{EXAMPLES[0]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[0]['response'])}
"""
    example_merge = f"""INPUT:
{EXAMPLES[1]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[1]['response'])}
"""
    example_keep = f"""INPUT:
{EXAMPLES[2]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[2]['response'])}
"""
    example_special = f"""INPUT:
{EXAMPLES[3]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[3]['response'])}
"""
    return MERGE_FACTS_PROMPT.format(
        example_replace=example_replace,
        example_merge=example_merge,
        example_keep=example_keep,
        example_special=example_special,
        tab=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
