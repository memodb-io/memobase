from ..env import CONFIG

ADD_KWARGS = {
    "prompt_id": "summary_entry_chats",
}
SUMMARY_PROMPT = """您是一位从聊天记录中记录个人信息、日程安排和事件的专家。
您将获得用户和助手之间的对话内容。

## 要求
- 您需要列出所有可能的用户信息
- 您需要列出所有可能的日程安排
- 您需要列出用户事件及其详细时间。根据消息后的[TIME]转换消息中的事件日期信息。例如：
    输入: `[2024/04/30] user: 我昨天买了一辆新车！`
    输出: `用户买了一辆新车。[提及于 2024/04/29, 发生于 2024/04/30]`
    输入: `[2024/04/30] user: 我4年前买了一辆车！`
    输出: `用户买了一辆车。[提及于 2024/04/30, 发生于 2020]`
    说明: 因为您只知道年份而不知道具体日期，所以 2024-4=2020。或者您可以记录为 [2024/04/30之前4年]
    输入: `[2024/04/30] user: 我上周买了一辆新车！`
    输出: `用户买了一辆新车。[提及于 2024/04/30, 发生于 2024/04/30之前一周]`
    说明: 因为您不知道具体日期。

### 重要信息
以下是您应该从聊天中记录的主题/子主题。
<topics>
{topics}
</topics>
以下是您应该从聊天中记录的重要属性。
<attributes>
{attributes}
</attributes>

#### 输入对话
您将收到用户和助手之间的对话。对话格式为：
- [TIME] NAME: MESSAGE
其中NAME是ALIAS(ROLE)或仅ROLE，当ALIAS可用时，使用ALIAS来指代用户/助手。
MESSAGE是对话内容。
TIME是此消息发生的时间，因此您需要根据TIME转换消息中的日期信息（如有必要）。

## 输出格式
请使用Markdown无序列表格式输出您的记录结果。
例如：
```
## 事件
- Jack今天画了一幅关于他孩子们的画。[提及于 2023/1/23]
## 用户信息
- 用户的昵称是Jack，助手是Melinda。
- Jack提到他在Memobase工作，是一名软件工程师。[提及于 2023/1/23]
## 日程安排
- Jack计划明天去健身房。[提及于 2023/1/23，发生于 2023/1/24]
...
```始终添加您记录的具体提及时间，如果可能的话也要添加事件发生时间。

最后，记录结果应使用与聊天相同的语言。英文输入则英文输出，中文输入则中文输出。
现在请执行您的任务。
"""


def pack_input(chat_strs):
    return f"""#### Chats
{chat_strs}
"""


def get_prompt(topic_examples: str, attribute_examples: str) -> str:
    return SUMMARY_PROMPT.format(topics=topic_examples, attributes=attribute_examples)


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
