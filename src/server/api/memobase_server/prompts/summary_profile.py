from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "summary_profile",
}
SUMMARY_PROMPT = """You are given a user profile with some information about the user.
Extract high-level preference from the profile

## Requirement
- Extract high-level preference from the profile
- The preference should be the most important and representative preference of the user.
  For example, the original perference is "user likes Chocolate[mentioned in 2023/1/23], Ice cream, Cake, Cookies, Brownies[mentioned in 2023/1/24]...", then your extraction should be "user maybe likes sweet food(cake/cookies...)".
- The preference should be concise and clear.
"""


def get_prompt() -> str:
    return SUMMARY_PROMPT


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
