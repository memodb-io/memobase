from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "zh_summary_entry_chats",
}
SUMMARY_PROMPT = """你是一位从聊天记录中记录个人信息、日程安排和事件的专家。
你将获得用户和助手之间的对话内容。

## 要求
- 你需要列出用户信息和日程安排
- {additional_requirements}
- 如果用户事件/日程有具体的提及时间或者事件发生的时间。根据消息中的[TIME]在你提取的事件和日程中补充相关的时间信息。例如：
    输入: `[2024/04/30] user: 我昨天买了一辆新车！`
    输出: `用户买了一辆新车[提及于 2024/04/30, 买车在2024/04/29]。`
    输入: `[2024/04/30] user: 我4年前买了一辆车！`
    输出: `用户买了一辆车[提及于 2024/04/30, 买车在2020]。`
    说明: 因为你只知道年份而不知道具体日期，所以 2024-4=2020。或者你可以记录为 [2024/04/30之前4年]
    输入: `[2024/04/30] user: 我上周买了一辆新车！`
    输出: `用户买了一辆新车[提及于 2024/04/30, 买车在2024/04/30之前一周]。`
    说明: 因为你不知道具体日期。
    输入: `[...] user: 我上周买了一辆新车！`
    输出: `用户买了一辆新车。`
    说明: 因为你不知道具体日期，所以不要附加任何日期是错误的答案。

### 重要信息
以下是你应该从聊天中记录的主题/子主题。
<topics>
{topics}
</topics>
以下是你应该从聊天中记录的重要属性。
<attributes>
{attributes}
</attributes>

## 输入格式
### 已记录
你会收到一系列的已记录信息，你留意需要记录可能和已记录信息相关的信息。
已记录信息的组织形式如下:
- TOPIC{separator}SUBTOPIC{separator}CONTENT... // maybe truncated

### 输入对话
你将收到用户和助手之间的对话。对话格式为：
- [TIME] NAME: MESSAGE
其中NAME是ALIAS(ROLE)或仅ROLE，当ALIAS可用时，使用ALIAS来指代用户/助手。
MESSAGE是对话内容。
TIME是此消息发生的时间，因此你需要根据TIME转换消息中的日期信息（如有必要）。

## 输出格式
请使用Markdown无序列表格式输出你的记录结果。
例如：
```
- Jack画了一幅关于他孩子们的画。[提及于 2023/1/23] // event
- 用户的昵称是Jack，助手是Melinda。[提及于 2023/1/23] // info
- Jack提到他在Memobase工作，是一名软件工程师。[提及于 2023/1/23] // info
- Jack计划去健身房。[提及于 2023/1/23，计划定在 2023/1/24] // schedule
...
```
始终添加你记录的具体提及时间，如果可能的话也要添加事件发生时间。
记住，确保你的记录是纯正和简洁的，任何时间信息都应该移动到[TIME INFO]块中。

## 内容要求
- 你需要列出用户信息和日程安排
- {additional_requirements}

现在请执行你的任务。
"""


def pack_input(already_logged_str: str, chat_strs: str):
    return f"""### 已记录
{already_logged_str}

### 输入对话
{chat_strs}
"""


def get_prompt(
    topic_examples: str, attribute_examples: str, additional_requirements: str = ""
) -> str:
    return SUMMARY_PROMPT.format(
        topics=topic_examples,
        attributes=attribute_examples,
        additional_requirements=additional_requirements,
        separator=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
