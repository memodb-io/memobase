from . import user_profile_topics
from .utils import pack_profiles_into_string
from ..models.response import AIUserProfiles
from ..env import CONFIG

ADD_KWARGS = {}
EXAMPLES = [
    (
        """
[2025/01/14] user: Hi, how is your day?
""",
        AIUserProfiles(**{"facts": []}),
    ),
    (
        """
[2025/01/01] user: I still can't believe we're married today!
[2025/01/01] SiLei: I know, it will be the most amazing journey of my life.
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "demographics",
                        "sub_topic": "marital_status",
                        "memo": "user is married to SiLei",
                    },
                    {
                        "topic": "life_event",
                        "sub_topic": "Marriage",
                        "memo": "Married to SiLei at 2025/01/01",
                    },
                ]
            }
        ),
    ),
    (
        """
[2025/01/01] user: Hi, I am looking for a daily restaurant in San Francisco cause I live there.
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "contact_info",
                        "sub_topic": "city",
                        "memo": "San Francisco",
                    }
                ]
            }
        ),
    ),
    (
        """
[2025/01/01] user: Can you give me a letter of references for my PhD applications?
[2025/01/01] assistant: Got it, Melinda!...
[2025/01/01] user: Thanks for remembering my name!
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "basic_info",
                        "sub_topic": "Name",
                        "memo": "Referred as Melinda",
                    },
                    {
                        "topic": "education",
                        "sub_topic": "Degree",
                        "memo": "user is applying PhD at the time: 2025/01/01",
                    },
                ]
            }
        ),
    ),
    (
        """
[2024/10/11] user: Yesterday, I had a meeting with John at 3pm. We discussed the new project.
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "work",
                        "sub_topic": "Collaboration",
                        "memo": "user is starting a project with John and already met once at 2024/10/10",
                    }
                ]
            }
        ),
    ),
    (
        """
[2025/01/01] user: Hi, my name is John. I am a software engineer at Memobase.
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
                        "memo": "user is a Software engineer",
                    },
                    {
                        "topic": "work",
                        "sub_topic": "Company",
                        "memo": "user works at Memobase",
                    },
                ]
            }
        ),
    ),
    (
        """
[2025/01/01] user: Me favorite movies are Inception and Interstellar.
[2025/01/01] assistant: Those are great movies, how about the movie: Tenet?
[2025/01/02] user: I have watched Tenet, I think that's my favorite in fact.
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "interest",
                        "sub_topic": "Movie",
                        "memo": "Inception, Interstellar and Tenet; favorite movie is Tenet",
                    },
                    {
                        "topic": "interest",
                        "sub_topic": "movie_director",
                        "memo": "user seems to be a Big fan of director Christopher Nolan",
                    },
                ]
            }
        ),
    ),
]

DEFAULT_JOB = """You are a professional psychologist.
Your responsibility is to carefully read out the conversation between the user and the other party.
Then extract relevant and important facts, preferences about the user that will help evaluate the user's state.
You will not only extract the information that's explicitly stated, but also infer what's implied from the conversation.
You will use the same language as the user's input to record the facts.
"""

FACT_RETRIEVAL_PROMPT = """{system_prompt}

## Topics you should be aware of
Below are some example topics/sub_topics you can refer to:
{user_profile_topics}
You can create your own topics/sub_topics if you find it necessary, Anything valuable to evaluate the user's state is welcomed.

## Formatting

### Input
You will receive a conversation between the user and the assistant. The format of the conversation is:
- [TIME] NAME: MESSAGE
where NAME is sometimes "user", sometimes "assistant" or other names.
MESSAGE is the content of the conversation. Understand the conversation and remember the time when the conversation happened.

### Output
You need to extract the facts and preferences from the conversation and place them in order list:
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


## User Before topics
Below are the topics and subtopics that the user has already shared with the assistant:
{before_topics}
consider use the same topic/subtopic if it's mentioned in the conversation again.

Following is a conversation between the user and the assistant. You have to extract/infer the relevant facts and preferences from the conversation and return them in the list format as shown above.
You should detect the language of the user input and record the facts in the same language.
If you do not find anything relevant facts, user memories, and preferences in the below conversation, just return "NONE" or "NO FACTS".
"""


def get_prompt(already_topics: str) -> str:
    sys_prompt = CONFIG.system_prompt or DEFAULT_JOB
    examples = "\n\n".join(
        [f"Input: {p[0]}Output:\n{pack_profiles_into_string(p[1])}" for p in EXAMPLES]
    )
    return FACT_RETRIEVAL_PROMPT.format(
        system_prompt=sys_prompt,
        before_topics=already_topics,
        examples=examples,
        tab=CONFIG.llm_tab_separator,
        user_profile_topics=user_profile_topics.get_prompt(),
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(
        get_prompt(
            "basic_info: Name: John\nwork: Title: Software engineer\nwork: Company: Memobase"
        )
    )
