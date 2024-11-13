from datetime import datetime

EXAMPLES = [
    {
        "old": """
<old_memo data_index=0>
    User is a software engineer
</old_memo>
""",
        "new": """
<new_memo data_index=0>
    User is John
</new_memo>
""",
        "response": """{
    "ADD": [{"new_index": 0}],
    "UPDATE": []
}
""",
    },
    {
        "old": """
<old_memo data_index=0>
    User like cheese pizza
</old_memo>
<old_memo data_index=1>
    User is a software engineer
</old_memo>
<old_memo data_index=2>
    User likes to play cricket
</old_memo>
""",
        "new": """
<new_memo data_index=0>
    Loves cheese pizza
</new_memo>
<new_memo data_index=1>
    Loves to play cricket with friends
</new_memo>
<new_memo data_index=2>
    User is John
</new_memo>
""",
        "response": """{
    "ADD": [{"new_index": 2}],
    "UPDATE": [
        {"old_index": 0, "new_index": 0, "memo": "User loves cheese pizza"},
        {"old_index": 2, "new_index": 1, "memo": "User loves to play cricket with friends"}
    ]
}
""",
    },
]

# Prompt is adapted from https://github.com/mem0ai/mem0
MERGE_FACTS_PROMPT = """You are a smart memo manager which controls the memory/figure of a user.
You should perform two operations: 
(1) add a new memo into the memory
(2) merge/archive a new memo with a existing memo in the memory
And return your results in JSON format, and Remeber the `data_index` of new memo and old memo to perform the right operation.

Compare newly retrieved facts with the existing memory. For each new fact, decide whether to:
- ADD: Add it to the memory as a new memo
- UPDATE: Update an existing memo

There are specific guidelines to select which operation to perform:

1. **ADD**: If the new memo contain new information not present in the old memos, then you have to add it into the current user memory:
   **Example**:
   {example_add}

2. **UPDATE**: If the new memo contain information that is already present in the memory, then you have to update/archive the old memo with the new one:
    - archive: If the new memo contains/imply information that conveys the same thing as the old memo present in the memory, then you have to keep the fact which has the most information. 
        Example -- if the old memo "Likes cheese pizza" and the new memo is "Loves cheese pizza", then you archive it because they convey the same information.
    - update: If the new memo contains/imply information that diffs from the corresponding old memo present in the memory, then you have to update the old memory by merging the new and old memo: 
        Example -- if the old memo "User likes to play cricket" and the new memo is "Loves to play cricket with friends", then update the memory to "User likes to play cricket with friends".
    - revise: If the new memo contains/implys information that is a revision/fixup of the old memo present in the memory, then you have to update the old memory by updating the new:
        Example -- if the old memo "User is 39 years old" and the new memo is "User is 40 years old", update the memory to "User is 40 years old".
        Example -- if the old memo contains "User lives in UK" and the new memo is "User is working in USA and enjoy the life there", update the memory to "User lives and works in USA".
    - **Example**:
      {example_update}

Understand the new memo wisely, you are allowed to infer the information from the new memo and old memo to decide the correct operation.      
The old and new memo will be given to you in XML format. The `data_index` will be used to identify the memo. Remeber the data_index of each memo to perform the correct operation.

Follow the instruction mentioned below:
- Do not return anything from the custom few shot prompts provided above.
- If the old memos is empty, then you have to add the new memos to the memory.
- Stick to the correct JSON format.
- To add a new memo, find the corresponding data_index of this new_memo and append it to "ADD" field.
- To update/archive a old memo with a new memo, find the corresponding data_index of this old_memo and new_memo, 
  generate the new version description of the memo and append it to "UPDATE" field.

Do not return anything except the JSON format.
"""


def get_prompt() -> str:
    example_add = f"""INPUT:
{EXAMPLES[0]['old']}
{EXAMPLES[0]['new']}
OUTPUT:
{EXAMPLES[0]['response']}
"""
    example_update = f"""INPUT:
{EXAMPLES[1]['old']}
{EXAMPLES[1]['new']}
OUTPUT:
{EXAMPLES[1]['response']}
"""
    return MERGE_FACTS_PROMPT.format(
        example_add=example_add, example_update=example_update
    )


if __name__ == "__main__":
    print(get_prompt())
