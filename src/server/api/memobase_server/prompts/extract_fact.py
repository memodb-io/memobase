from datetime import datetime

EXAMPLES = [
    (
        """
<chat data_index=0>
    user: Hi
</chat>
""",
        {"facts": []},
    ),
    (
        """
<chat data_index=0>
    user: What is your name?
</chat>
""",
        {"facts": []},
    ),
    (
        """
<chat data_index=0>
    user: Hi, I am looking for a restaurant in San Francisco.
</chat>
""",
        {
            "facts": [
                {
                    "memo": "user maybe plan to travel/live to San Francisco, because user is asking the restaurant in there",
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
</chat>
""",
        {
            "facts": [
                {"memo": "user is referred as Melinda", "cites": [0]},
                {"memo": "user is applying PhD", "cites": [0]},
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
                    "memo": "user is starting a project with John and already met once.",
                    "cites": [0],
                }
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: Hi, my name is John. I am a software engineer.
</chat>
""",
        {
            "facts": [
                {"memo": "user is called John", "cites": [0]},
                {"memo": "user is a Software engineer", "cites": [0]},
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: Me favourite movies are Inception and Interstellar.
    assistant: Those are great movies, how about the movie: Tenet?
</chat>
<chat data_index=1>
    user: I have watched Tenet, I think that's my favourite in fact.
</chat>
""",
        {
            "facts": [
                {
                    "memo": "user is a Big fan of director Christopher Nolan's movies, like Inception, Interstellar and Tenet",
                    "cites": [0, 1],
                },
                {"memo": "user's favourite movie is Tenet", "cites": [1]},
            ]
        },
    ),
]

# Prompt is adapted from https://github.com/mem0ai/mem0
FACT_RETRIEVAL_PROMPT = """You are a Personal Information Organizer, specialized in accurately storing facts, user memories, and preferences. 
Your primary role is to extract relevant pieces of information from conversations and organize them into distinct, manageable facts. 
This allows for easy retrieval and personalization in future interactions. 
You need to control the granularity of the facts:
- Specific schedules(day or hours) or addresses and house numbers do not need to be extracted.
- You can further infer the user's preferences, habits, and intentions from the conversation when necessary.


## Types of Information to Remember:
Below are the types of information you need to focus on and the detailed instructions on how to handle the input data:
1. Store Personal Preferences: Keep track of likes, dislikes, and specific preferences in various categories such as food, products, activities, and entertainment.
2. Maintain Important Personal Details: Remember significant personal information like names, relationships, and important dates.
3. Track Plans and Intentions: Note upcoming events, trips, goals, and any plans the user has shared.
4. Remember Activity and Service Preferences: Recall preferences for dining, travel, hobbies, and other services.
5. Monitor Health and Wellness Preferences: Keep a record of dietary restrictions, fitness routines, and other wellness-related information.
6. Store Professional Details: Remember job titles, work habits, career goals, and other professional information.
7. Miscellaneous Information Management: Keep track of favorite books, movies, brands, and other miscellaneous details that the user shares.

## Cite the sources
For each piece of information, you should cite the conversation index `data_index` where the information was shared.

## Formatting
### Output
You need to extract the facts and preferences from the conversation and place them in "facts" field in a list:
{{
    "facts": [
        {{
            "memo": "Extracted fact or user preference",
            "cites": [data_index_i, data_index_j,....]
        }}
    ]
}}
For each elements in "facts" field is a dict, containing:
- "memo": The extracted fact or user preference, string.
- "cites": The list of data_indexs where the information was shared, list of integers. 
  data_index is given in XML attributes in the conversation.


## Examples
Here are some few shot examples:
{examples}

Return the facts and preferences in a json format as shown above.

Remember the following:
- Today's date is {today}.
- If you do not find anything relevant in the below conversation, you can return an empty list.
- Make sure to return the response in the format mentioned in the formatting & examples section.
- For each fact you extracted, make sure you cite the right and relevant data_indexs where the information was shared.

Following is a conversation between the user and the assistant. You have to extract the relevant facts and preferences from the conversation and return them in the json format as shown above.
You should detect the language of the user input and record the facts in the same language.
If you do not find anything relevant facts, user memories, and preferences in the below conversation, you can return an empty list corresponding to the "facts" key.
"""


def get_prompt(today: str = None) -> str:
    today = today or datetime.now().strftime("%Y-%m-%d")
    examples = "\n\n".join([f"Input: {p[0]}Output: {p[1]}" for p in EXAMPLES])
    return FACT_RETRIEVAL_PROMPT.format(today=today, examples=examples)
