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
**Example**:
{example_replace}

## merge the memos
Note that MERGE should be selected as long as there is information in the old memo that is not included in the new memo.
The old and new memo tell different parts of the same story and should be merged together:
**Example**:
{example_merge}

## keep the old one
If the new memo has no information added or containing nothing useful, you should keep the old memo.
**Example**:
{example_keep}

Understand the memos wisely, you are allowed to infer the information from the new memo and old memo to decide the final memo.
Follow the instruction mentioned below:
- Do not return anything from the custom few shot prompts provided above.
- Stick to the correct format.
- Make sure the final memo is no more than 5 sentences.
- Always concise and output the guts of the memo.
"""


def get_input(topic, subtopic, old_memo, new_memo):
    return f"""
## User Topic
{topic}, {subtopic}
## Old Memo
{old_memo}
## New Memo
{new_memo}
"""


def get_prompt() -> str:
    example_add = f"""INPUT:
{EXAMPLES[0]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[0]['response'])}
"""
    example_update = f"""INPUT:
{EXAMPLES[1]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[1]['response'])}
"""
    example_keep = f"""INPUT:
{EXAMPLES[2]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[2]['response'])}
"""
    return MERGE_FACTS_PROMPT.format(
        example_replace=example_add,
        example_merge=example_update,
        example_keep=example_keep,
        tab=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
