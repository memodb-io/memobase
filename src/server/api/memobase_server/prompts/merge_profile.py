from datetime import datetime

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
            "action": "REPLACE",
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
            "action": "MERGE",
            "memo": "Love cheese and chicken pizza",
        },
    },
]

MERGE_FACTS_PROMPT = """You are a smart memo manager which controls the memory/figure of a user.
You will be given two memos, one old and one new on the same topic/aspect of the user.
Your decision space is below: 
(1) REPLACE: Replace the old memo with the new memo
(2) MERGE: Merge the old memo with the new memo
Place your action in 'action' field and the final memo in 'memo' field.
And return your results in JSON format.

Compare newly retrieved facts with the existing memory. For each new fact, decide whether to:
- REPLACE: The old memo is considered completely outdated and should be replaced with the new memo, or the new memo is completely conflicting with the old memo.
- MERGE: The old and new memo tell different parts of the same story and should be merged together.

There are specific guidelines to select which operation to perform:


## REPLACE
The old memo is considered outdated and should be replaced with the new memo, or the new memo is conflicting with the old memo:
**Example**:
{example_replace}

## MERGE
The old and new memo tell different parts of the same story and should be merged together:
**Example**:
{example_merge}

Understand the memos wisely, you are allowed to infer the information from the new memo and old memo to decide the correct operation.
Follow the instruction mentioned below:
- Do not return anything from the custom few shot prompts provided above.
- Stick to the correct JSON format.

Do not return anything except the JSON format.
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
{EXAMPLES[0]['response']}
"""
    example_update = f"""INPUT:
{EXAMPLES[1]['input']}
OUTPUT:
{EXAMPLES[1]['response']}
"""
    return MERGE_FACTS_PROMPT.format(
        example_replace=example_add, example_merge=example_update
    )


if __name__ == "__main__":
    print(get_prompt())
