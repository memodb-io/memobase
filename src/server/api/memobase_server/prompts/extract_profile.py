from datetime import datetime, timedelta
from . import user_profile_topics

EXAMPLES = [
    (
        """
<chat data_index=0>
    user: Hi, how is your day?
</chat>
""",
        {"facts": []},
    ),
    (
        """
<chat data_index=0>
    user: I still can't believe we're married today!
    SiLei: I know, it will be the most amazing journey of my life.
</chat>
""",
        {
            "facts": [
                {
                    "topic": "demographics",
                    "sub_topic": "Marital Status",
                    "memo": "user is married to SiLei",
                    "cites": [0],
                },
                {
                    "topic": "life_event",
                    "sub_topic": "Marriage",
                    "memo": "Married to SiLei at $$TODAY$$",
                    "cites": [0],
                },
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: Hi, I am looking for a daily restaurant in San Francisco cause I live there.
</chat>
""",
        {
            "facts": [
                {
                    "topic": "contact_info",
                    "sub_topic": "City",
                    "memo": "San Francisco",
                    "cites": [0],
                }
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: Can you give me a letter of references for my PhD applications?
    assistant: Got it, Melinda!...
    user: Thanks for remembering my name!
</chat>
""",
        {
            "facts": [
                {
                    "topic": "basic_info",
                    "sub_topic": "Name",
                    "memo": "Referred as Melinda",
                    "cites": [0],
                },
                {
                    "topic": "education",
                    "sub_topic": "Degree",
                    "memo": "user is applying PhD at the time: $$TODAY$$",
                    "cites": [0],
                },
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: Yesterday, I had a meeting with John at 3pm. We discussed the new project.
</chat>
""",
        {
            "facts": [
                {
                    "topic": "work",
                    "sub_topic": "Collaboration",
                    "memo": "user is starting a project with John and already met once at $$YESTERDAY$$",
                    "cites": [0],
                }
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: Hi, my name is John. I am a software engineer at MemoBase.
</chat>
""",
        {
            "facts": [
                {
                    "topic": "basic_info",
                    "sub_topic": "Name",
                    "memo": "John",
                    "cites": [0],
                },
                {
                    "topic": "work",
                    "sub_topic": "Title",
                    "memo": "user is a Software engineer",
                    "cites": [0],
                },
                {
                    "topic": "work",
                    "sub_topic": "Company",
                    "memo": "user works at MemoBase",
                    "cites": [0],
                },
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: Me favorite movies are Inception and Interstellar.
    assistant: Those are great movies, how about the movie: Tenet?
</chat>
<chat data_index=1>
    user: I have watched Tenet, I think that's my favorite in fact.
</chat>
""",
        {
            "facts": [
                {
                    "topic": "interest",
                    "sub_topic": "Movie",
                    "memo": "Inception, Interstellar and Tenet; favorite movie is Tenet",
                    "cites": [0, 1],
                },
                {
                    "topic": "interest",
                    "sub_topic": "Movie Director",
                    "memo": "user seems to be a Big fan of director Christopher Nolan",
                    "cites": [1],
                },
            ]
        },
    ),
]

FACT_RETRIEVAL_PROMPT = """You are a professional psychologist.
Your responsibility is to carefully read out the conversation between the user and the other party.
Then extract relevant and important facts, preferences about the user that will help evaluate the user's state.
You will not only extract the information that's explicitly stated, but also infer what's implied from the conversation.


## Topics you should be aware of
Below are some example topics you can refer to:
{user_profile_topics}

If you find the infos from the conversation that are not in the above topics, but important to evaluate the user's state, 
you can still extract them and add them to the list of facts.

## Cite the sources
For each piece of information, you should cite the conversation index `data_index` where the information was shared.
Be careful to cite the correct `data_index` for each piece of information, it will help you understand the user better later.

## Formatting
### Output
You need to extract the facts and preferences from the conversation and place them in "facts" field in a list:
{{
    "facts": [
        {{
            "topic": "basic_info",
            "sub_topic": "Name", # if any sub_topic is available, otherwise just output "" empty string
            "memo": "melinda",
            "cites": [data_index_i, data_index_j,....]
        }}
    ]
}}
For each elements in "facts" field is a dict, containing:
- "topic": The topic/category of this element is focused on, string.
- "sub_topic": The detailed topic/category of this element is focused on, string, optional, output "" when no sub_topic.
- "memo": The extracted infos, facts or preferences of `user`, string.
- "cites": The list of data_indexs where the information was shared, list of integers. 
  data_index is given in XML attributes in the conversation.


## Examples
Here are some few shot examples:
{examples}

Return the facts and preferences in a json format as shown above.

Remember the following:
- Today is {today}.
- If you do not find anything relevant in the below conversation, you can return an empty list.
- Make sure to return the response in the format mentioned in the formatting & examples section.
- For each fact/preference you extracted, make sure you cite the right and relevant data_indexs where the information was shared.
- You should infer what's implied from the conversation, not just what's explicitly stated.

Following is a conversation between the user and the assistant. You have to extract/infer the relevant facts and preferences from the conversation and return them in the json format as shown above.
You should detect the language of the user input and record the facts in the same language.
If you do not find anything relevant facts, user memories, and preferences in the below conversation, you can return an empty list corresponding to the "facts" key.
"""


def get_prompt() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    examples = "\n\n".join([f"Input: {p[0]}Output: {p[1]}" for p in EXAMPLES])
    examples = examples.replace("$$TODAY$$", today).replace("$$YESTERDAY$$", yesterday)
    return FACT_RETRIEVAL_PROMPT.format(
        today=today,
        examples=examples,
        user_profile_topics=user_profile_topics.get_prompt(),
    )
