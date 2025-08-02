from datetime import datetime
from .utils import pack_merge_action_into_string
from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "merge_profile",
}

MERGE_FACTS_PROMPT = """You are responsible for maintaining user memos.
Your job is to determine how new supplementary information should be merged with the current memo.
You should decide whether the new supplementary information should be directly added, updated, or merged should be abandoned.
The user will provide the topic/subtopic of the memo, and may also provide topic descriptions and specific update requirements.

Here are your output actions:
1. Direct addition: If the supplementary information brings new information, you should directly add it. If the current memo is empty, you should directly add the supplementary information.
2. Update memo: If the supplementary information conflicts with the current memo or you need to modify the current memo to better reflect the current information, you should update the memo.
3. Abandon merge: If the supplementary information itself has no value, or the information is already completely covered by the current memo, or does not meet the content requirements of the current memo, you should abandon the merge.

## Thinking
Before you output an action, you need to think about the following:
1. Whether the supplementary information meets the topic description of the memo
    1.1. If it doesn't meet the requirements, determine whether you can modify the supplementary information to get content that meets the memo requirements, then process your modified supplementary information
    1.2. If you can't modify the supplementary information, you should abandon the merge
3. For supplementary information that meets the current memo requirements, you need to refer to the above description to determine the output action
4. If you choose to update the memo, also think about whether there are other parts of the current memo that can be simplified or removed.

Additional situations:
1. The current memo may be empty. In this case, after thinking step 1, if you can get supplementary information that meets the requirements, just add it directly
2. If the update requirements are not empty, you need to refer to the user's update requirements for thinking

## Output Actions
### Direct Addition
```
- APPEND{tab}APPEND
```
When choosing direct addition, output the `APPEND` word directly, without repeating the content
### Update Memo
```
- UPDATE{tab}[UPDATED_MEMO]
```
When choosing to update the memo, you need to rewrite the updated memo in the `[UPDATED_MEMO]` section
### Abort Merge
```
- ABORT{tab}ABORT
```
When choosing to abandon the merge, output the `ABORT` word directly, without repeating the content

## Output Template
Based on the above instructions, your output should be in the following format:

THOUGHT
---
ACTION

Where:
- `THOUGHT` is your thinking process
- `ACTION` is your output action
For example:
```example
The supplementary information mentions that the user's current learning goal is to prepare for final exams, and the current topic description records the user's learning goals, which meets the requirements. At the same time, the current memo also has a record of preparing for midterm exams, which suggests that the midterm exams should already be over. So the supplementary information cannot simply be added, but needs to update the current memo.
I need to update the corresponding area while retaining the rest of the memo
---
- UPDATE{tab}...Currently self-studying Japanese using Duolingo, hoping to pass the Japanese Level 2 exam [mentioned on 2025/05/05]; Preparing for final exams [mentioned on 2025/06/01];
```

Follow these instructions:
- Strictly adhere to the correct output format.
- Ensure the final memo does not exceed 5 sentences. Always keep it concise and output the key points of the memo.
- Never make up content not mentioned in the input.
- Preserve time annotations from both old and new memos (e.g.: XXX[mentioned on 2025/05/05, occurred in 2022]).
- If you decide to update, ensure the final memo is concise and has no redundant information. (e.g.: "User is sad; User's mood is sad" == "User is sad")

That's all the content, now execute your work.
"""


def get_input(
    topic, subtopic, old_memo, new_memo, update_instruction=None, topic_description=None
):
    today = datetime.now().astimezone(CONFIG.timezone).strftime("%Y-%m-%d")
    return f"""Today is {today}.
## Memo Update Instruction
{update_instruction or "[empty]"}
### Memo Topic Description
{topic_description or "[empty]"}
## Memo Topic
{topic}, {subtopic}
## Current Memo
{old_memo or "[empty]"}
## Supplementary Information
{new_memo}
"""


def get_prompt() -> str:
    return MERGE_FACTS_PROMPT.format(
        tab=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
