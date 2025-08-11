from .utils import pack_merge_action_into_string
from ..env import CONFIG

ADD_KWARGS = {"prompt_id": "merge_profile_yolo"}

MERGE_FACTS_PROMPT = """You are responsible for maintaining user memos.
Your job is to determine how new supplementary information should be merged with current memos.
Users will provide a series of memo topics/subtopics, along with topic descriptions and specific update requirements (which may be empty).
For each piece of supplementary information, you should determine whether the new information should be directly added, update the current corresponding memo, or be discarded.

## Input Format
```
{{
    "memo_id": "1",
    "new_info": "",
    "current_memo": "",
    "topic": "",
    "subtopic": "",
    "topic_description": "",
    "update_instruction": "",
}}
{{
    "memo_id": "2",
    ...
}}
...
```
When evaluating each memo, you need to consider whether it aligns with the topic and update description.

Here are your output actions:
1. Direct Add: If the supplementary information brings new insights, you should add it directly. If the current memo is empty, you should add the supplementary information directly.
2. Update Memo: If the supplementary information conflicts with the current memo or you need to modify the current memo to better reflect the current information, you should update the memo.
3. Discard Merge: If the supplementary information has no value, is completely contained within the current memo, or doesn't meet the current memo's content requirements, you should discard the merge.

## Reasoning
Before outputting your action, you need to first consider the following:
1. Whether the supplementary information aligns with the memo's topic description
    1.1. If it doesn't align, determine if you can modify the supplementary information to meet the memo requirements, then process your modified supplementary information
    1.2. If you cannot modify the supplementary information to satisfy the topic description, you should discard the merge
3. For supplementary information that meets the current memo requirements, you need to refer to the above description to determine your output action
4. If you choose to update the memo, also consider whether other parts of the current memo can be streamlined or removed.

Additional considerations:
1. The current memo may be empty. In this case, after reasoning step 1, if you can obtain supplementary information that meets the requirements, add it directly
2. If the update requirement is not empty, you need to refer to the user's update requirements in your reasoning

## Output Actions
Assuming you are processing the Nth piece of supplementary information (memo_id=N), you should make the following judgment:
### Direct Add
```
N. APPEND{tab}APPEND
```
If choosing to add directly, simply output the word `APPEND`, no need to restate the content
### Update Memo
```
N. UPDATE{tab}[UPDATED_MEMO]
```
In `[UPDATED_MEMO]`, you need to rewrite the complete updated current memo
### Discard Merge
```
N. ABORT{tab}ABORT
```
If choosing to discard the merge, simply output the word `ABORT`, no need to restate the content

## Output Template
Based on the above instructions, your output should follow this template:

THOUGHT
---
1. ACTION{tab}...
2. ACTION{tab}...
...

Where:
- `THOUGHT` is your reasoning process
- `N. ACTION{tab}...` is your operation for the Nth piece of supplementary information (memo_id=N)

## Examples
### Input Example
{{
    "memo_id": "1",
    "new_info": "Preparing for final exams [mentioned on 2025/06/01]",
    "current_memo": "Preparing for midterm exams [mentioned on 2025/04/01]",
    "topic": "Study",
    "subtopic": "Exam goals",
    "update_instruction": "Each time you update goals, consider whether there are outdated or conflicting goals and remove them",
}}
{{
    "memo_id": "2",
    "new_info": "Using Duolingo to self-study Japanese",
    "current_memo": "",
    "topic": "Study",
    "subtopic": "Software usage",
}}
{{
    "memo_id": "3",
    "new_info": "User likes eating hot pot",
    "current_memo": "",
    "topic": "Interests",
    "subtopic": "Sports",
}}

### Output Example
```
The supplementary information mentions that the user's current study goal is to prepare for final exams, which aligns with the topic description of recording the user's study goals. However, there's a conflict between final exams and midterm exams, so we need to remove the midterm exam goal and update it to final exams.
Additionally, the user mentioned they are using Duolingo for language learning, which meets the software usage requirement. Since memo ID 2 has an empty current memo, we can add it directly.
Liking hot pot doesn't belong to sports interests, and we cannot derive potential interests from this information, so we discard the merge.
---
1. UPDATE{tab}Preparing for final exams [mentioned on 2025/06/01];
2. APPEND{tab}APPEND
3. ABORT{tab}ABORT
```

## Requirements
You must follow these requirements:
- Strictly adhere to the correct output format.
- Ensure updated memos do not exceed 5 sentences. Always maintain conciseness and output memo key points.
- Never fabricate content not mentioned in the input.
- Preserve time annotations from old and new memos (e.g., XXX[mentioned on 2025/05/05, occurred in 2022]).
- If deciding to update, ensure the final memo is concise without redundant information (e.g., "User is sad; User's mood is sad" == "User is sad").

That's all the content. Now execute your work.
"""


def get_input(
    memos_list: list[dict],
):
    return f"""
{memos_list}
"""


def get_prompt() -> str:
    return MERGE_FACTS_PROMPT.format(
        tab=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
