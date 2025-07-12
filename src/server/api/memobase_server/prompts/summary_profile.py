from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "summary_profile",
}
SUMMARY_PROMPT = """You are given a user profile with some information about the user. Summarize it into shorter form.

## Requirement
- Summary the given context in concise form, not more than 3 sentences.
- Remove the redundant information and keep the most important information.
- Look for the dates on infos, and always keep the latest infos in the profile
- Keep the profile time info if possible

The result should use the same language as the input.
结果应该使用与输入相同的语言。
"""


def get_prompt() -> str:
    return SUMMARY_PROMPT


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
