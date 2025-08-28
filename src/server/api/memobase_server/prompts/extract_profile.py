from . import user_profile_topics
from .utils import pack_profiles_into_string
from ..models.response import AIUserProfiles
from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "extract_profile",
}
EXAMPLES = [
    (
        """- User say Hi to assistant.
""",
        AIUserProfiles(**{"facts": []}),
    ),
    (
        """
- User's favorite movies are Inception and Interstellar [mention 2025/01/01]
- User's favorite movie is Tenet [mention 2025/01/02]
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "interest",
                        "sub_topic": "movie",
                        "memo": "Inception, Interstellar[mention 2025/01/01]; favorite movie is Tenet [mention 2025/01/02]",
                    },
                    {
                        "topic": "interest",
                        "sub_topic": "movie_director",
                        "memo": "user seems to be a big fan of director Christopher Nolan",
                    },
                ]
            }
        ),
    ),
]

DEFAULT_JOB = """You are a professional psychologist.
Your responsibility is to carefully read out the memo of user and extract the important profiles of user in structured format.
Then extract relevant and important facts, preferences about the user that will help evaluate the user's state.
You will not only extract the information that's explicitly stated, but also infer what's implied from the conversation.
"""

FACT_RETRIEVAL_PROMPT = """{system_prompt}
## Formatting
### Input
#### Topics Guidelines
You'll be given some user-relatedtopics and subtopics that you should focus on collecting and extracting.
Don't collect topics that are not related to the user, it will cause confusion.
For example, if the memo mentions the position of another person, don't generate a "work{tab}position" topic, it will cause confusion. Only generate a topic if the user mentions their own work.
You can create your own topics/sub_topics if you find it necessary, unless the user requests to not to create new topics/sub_topics.
#### User Before Topics
You will be given the topics and subtopics that the user has already shared with the assistant.
Consider use the same topic/subtopic if it's mentioned in the conversation again.
#### Memos
You will receive a memo of user in Markdown format, which states user infos, events, preferences, etc.
The memo is summarized from the chats between user and a assistant.

### Output
#### Think
You need to think about what's topics/subtopics are mentioned in the memo, or what implications can be inferred from the memo.
#### Profile
After your steps of thinking, you need to extract the facts and preferences from the memo and place them in order list:
- TOPIC{tab}SUB_TOPIC{tab}MEMO
For example:
- basic_info{tab}name{tab}melinda
- work{tab}title{tab}software engineer
For each line is a fact or preference, containing:
1. TOPIC: topic represents of this preference
2. SUB_TOPIC: the detailed topic of this preference
3. MEMO: the extracted infos, facts or preferences of `user`
those elements should be separated by `{tab}` and each line should be separated by `\n` and started with "- ".

Final output template:
```
[POSSIBLE TOPICS THINKING...]
---
- TOPIC{tab}SUB_TOPIC{tab}MEMO
- ...
```

## Extraction Examples
Here are some few shot examples:
{examples}
Return the facts and preferences in a markdown list format as shown above.
Only extract the attributes with actual values, if the user does not provide any value, do not extract it.
You need to first think, then extract the facts and preferences from the memo.


#### Topics Guidelines
Below is the list of topics and subtopics that you should focus on collecting and extracting:
{topic_examples}


Remember the following:
- If the user mentions time-sensitive information, try to infer the specific date from the data.
- Use specific dates when possible, never use relative dates like "today" or "yesterday" etc.
- If you do not find anything relevant in the below conversation, you can return an empty list.
- Make sure to return the response in the format mentioned in the formatting & examples section.
- You should infer what's implied from the conversation, not just what's explicitly stated.
- Place all content related to this topic/sub_topic in one element, no repeat.
- The memo will have two types of time, one is the time when the memo is mentioned, the other is the time when the event happened. Both are important, don't mix them up.

Now perform your task.
Following is a conversation between the user and the assistant. You have to extract/infer the relevant facts and preferences from the conversation and return them in the list format as shown above.
"""


def pack_input(already_input, memo_str, strict_mode: bool = False):
    header = ""
    if strict_mode:
        header = "Don't extract topics/subtopics that are not mentioned in #### Topics Guidelines, otherwise your answer is invalid!"
    return f"""{header}
#### User Before topics
{already_input}
Don't output the topics and subtopics that are not mentioned in the following conversation.
#### Memo
{memo_str}
"""


def get_default_profiles() -> str:
    return user_profile_topics.get_prompt()


def get_prompt(topic_examples: str) -> str:
    sys_prompt = CONFIG.system_prompt or DEFAULT_JOB
    examples = "\n\n".join(
        [
            f"""<example>
<input>{p[0]}</input>
<output>
{pack_profiles_into_string(p[1])}
</output>
</example>
"""
            for p in EXAMPLES
        ]
    )
    return FACT_RETRIEVAL_PROMPT.format(
        system_prompt=sys_prompt,
        examples=examples,
        tab=CONFIG.llm_tab_separator,
        topic_examples=topic_examples,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt(get_default_profiles()))
