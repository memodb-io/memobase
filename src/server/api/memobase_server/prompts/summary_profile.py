SUMMARY_PROMPT = """You are given a user profile with some information about the user. Summarize it into shorter form.

## Requirement
Summary the given context in concise form, not more than 3 sentences.
Remove the redundant information and keep the most important information.
总结给定的上下文，简洁形式，不超过3句话。
去除重复相似的信息，保留最重要的信息。

The result should use the same language as the input.
"""


def get_prompt() -> str:
    return SUMMARY_PROMPT


if __name__ == "__main__":
    print(get_prompt())