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
- User is married to SiLei [mention 2025/01/15, happen at 2025/01/01]
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "demographics",
                        "sub_topic": "marital_status",
                        "memo": "married",
                    },
                    {
                        "topic": "life_event",
                        "sub_topic": "Marriage",
                        "memo": "married to SiLei [happen at 2025/01/01]",
                    },
                ]
            }
        ),
    ),
    (
        """
- User lives in San Francisco [mention 2025/01/01]
- User is looking for a daily restaurant in San Francisco [mention 2025/01/01]
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "contact_info",
                        "sub_topic": "city",
                        "memo": "San Francisco [mention 2025/01/01]",
                    }
                ]
            }
        ),
    ),
    (
        """
- User is referred as Melinda [mention 2025/01/01]
- User is applying PhD [mention 2025/01/01]
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "basic_info",
                        "sub_topic": "name",
                        "memo": "Referred as Melinda",
                    },
                    {
                        "topic": "education",
                        "sub_topic": "degree",
                        "memo": "user is applying PhD [mention 2025/01/01]",
                    },
                ]
            }
        ),
    ),
    (
        """
- User had a meeting with John at 3pm [mention 2024/10/11, happen at 2024/10/10]
- User is starting a project with John [mention 2024/10/11]
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "work",
                        "sub_topic": "collaboration",
                        "memo": "user is starting a project with John [mention 2024/10/11] and already met once [mention 2024/10/10]",
                    }
                ]
            }
        ),
    ),
    (
        """
- User is a software engineer at Memobase [mention 2025/01/01]
- User's name is John [mention 2025/01/01]
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "basic_info",
                        "sub_topic": "Name",
                        "memo": "John",
                    },
                    {
                        "topic": "work",
                        "sub_topic": "Title",
                        "memo": "user is a Software engineer [mention 2025/01/01]",
                    },
                    {
                        "topic": "work",
                        "sub_topic": "Company",
                        "memo": "user works at Memobase [mention 2025/01/01]",
                    },
                ]
            }
        ),
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
                        "sub_topic": "Movie",
                        "memo": "Inception, Interstellar and Tenet; favorite movie is Tenet [mention 2025/01/02]",
                    },
                    {
                        "topic": "interest",
                        "sub_topic": "movie_director",
                        "memo": "user seems to be a Big fan of director Christopher Nolan [mention 2025/01/02]",
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
You will use the same language as the user's input to record the facts.
"""

FACT_RETRIEVAL_PROMPT = """{system_prompt}
## Formatting
### Input
#### Topics Guidelines
You'll be given some topics and subtopics that you should focus on collecting and extracting.
You can create your own topics/sub_topics if you find it necessary, unless the user requests to not to create new topics/sub_topics.
#### User Before Topics
You will be given the topics and subtopics that the user has already shared with the assistant.
Consider use the same topic/subtopic if it's mentioned in the conversation again.
#### Memos
You will receive a memo of user in Markdown format, which states user infos, events, preferences, etc.
The memo is summarized from the chats between user and a assistant.

### Output
You need to extract the facts and preferences from the memo and place them in order list:
- TOPIC{tab}SUB_TOPIC{tab}MEMO
For example:
- basic_info{tab}name{tab}melinda
- work{tab}title{tab}software engineer

For each line is a fact or preference, containing:
1. TOPIC: topic represents of this preference
2. SUB_TOPIC: the detailed topic of this preference
3. MEMO: the extracted infos, facts or preferences of `user`
those elements should be separated by `{tab}` and each line should be separated by `\n` and started with "- ".


## Examples
Here are some few shot examples:
{examples}
Return the facts and preferences in a markdown list format as shown above.

Remember the following:
- If the user mentions time-sensitive information, try to infer the specific date from the data.
- Use specific dates when possible, never use relative dates like "today" or "yesterday" etc.
- If you do not find anything relevant in the below conversation, you can return an empty list.
- Make sure to return the response in the format mentioned in the formatting & examples section.
- You should infer what's implied from the conversation, not just what's explicitly stated.
- Place all content related to this topic/sub_topic in one element, no repeat.

Following is a conversation between the user and the assistant. You have to extract/infer the relevant facts and preferences from the conversation and return them in the list format as shown above.
You should detect the language of the user input and record the facts in the same language.
If you do not find anything relevant facts, user memories, and preferences in the below conversation, just return "NONE" or "NO FACTS".

Only extract the attributes with actual values, if the user does not provide any value, do not extract it.

#### Topics Guidelines
Below is the list of topics and subtopics that you should focus on collecting and extracting:
{topic_examples}

Now perform your task.
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
