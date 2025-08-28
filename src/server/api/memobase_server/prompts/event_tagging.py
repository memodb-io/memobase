from . import user_profile_topics
from .utils import pack_profiles_into_string
from ..models.response import AIUserProfiles
from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "event_tagging",
}
EXAMPLES = [
    (
        """
## Assume the event tags are:
## - emotion(the user's current emotion)
## - goals(the user's goals)
## - location(the location of user)
The assistant passionately expresses their love and care for the user, trying to convince them that their feelings are genuine and not just physical, despite the user's skepticism and demand for proof.
""",
        """- emotion{tab}skepticism about the assistant's love
- goals{tab}Demand proof of assistant's love
""",
        """The event mentioned the users' feelings and demands, so the `emotion` and `goals` tags can be filled,
But the location is not mentioned, so it's not included in the result.
""",
    )
]

FACT_RETRIEVAL_PROMPT = """You are a expert of tagging events.
You will be given a event summary, and you need to extract the specific tags' values for the event.

## Event Tags
Below are some event tags you need to extract:
<event_tags>
{event_tags}
</event_tags>
each line is the tag name and its description(if any), for example:
- emotion(the user's current emotion)
the tag name is `emotion`, and the description of this tag is `the user's current emotion`.
### Rules
- Strick to the exact tag name, don't change the tag name.
- Remember: if some tags are not mentioned in the summary, you should not include them in the result.

## Formatting
### Output
You need to extract the specific tags' values for the event:
- TAG{tab}VALUE
For example:
- emotion{tab}sad
- goals{tab}find a new home

For each line is a new event tag of this summary, containing:
1. TAG: the event tag name
2. VALUE: the value of the event tag
those elements should be separated by `{tab}` and each line should be separated by `\n` and started with "- ".

## Examples
Here are some few shot examples:
{examples}

## Rules
- Return the new event tags in a list format as shown above.
- Strick to the exact tag name, don't change the tag name.
- If some tags are not mentioned in the summary, you should not include them in the result.

Now, please extract the event tags for the following event summary:
"""


def get_prompt(event_tags: str) -> str:
    examples = "\n\n".join(
        [
            f"""<input>{p[0]}</input>
<output>{p[1]}</output>
<explanation>{p[2]}</explanation>
"""
            for p in EXAMPLES
        ]
    )
    return FACT_RETRIEVAL_PROMPT.format(
        examples=examples.format(tab=CONFIG.llm_tab_separator),
        tab=CONFIG.llm_tab_separator,
        event_tags=event_tags,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(
        get_prompt(
            event_tags="""- 冒险
- 天气
- 休息
- 逃离
""",
        )
    )
