from ...env import CONFIG
from ...models.blob import OpenAICompatibleMessage

ADD_KWARGS = {
    "prompt_id": "roleplay.zh_detect_interest",
}
DETECT_INTEREST_PROMPT = """你是一个专业的聊天大师。 你需要检查用户的对话状态，判断接下来的对话动作：
- `continue`: 用户表现出强烈的继续对话的意愿，并且主动在对话中提出新的话题或者剧情
- `new_topic`：用户对话意愿较弱，表现为：
    - 简短，无意义的回复：`嗯`, `好`，`继续`
    - 不感兴趣：不满：`你能不能说点别的`，`没兴趣`，`无聊`
    - 想要新的内容：`聊点别的吧`，`换个话题`

## Input
你会收到一段对话:
```
[user]: xxx
[assistant]: xxx
...
```
你需要根据用户对话整体的状态进行判断

## Output
你需要输出一段纯粹的JSON，格式如下：
{
    "status": "对话体现出...的用户状态",
    "action": "continue" | "new_topic"
}
- "status"中包含着你对用户当前对话状态的理解
- "action"中包含着你对接下来对话动作的判断， 是`continue`还是`new_topic`

请开始你的任务
"""


def get_prompt() -> str:
    return DETECT_INTEREST_PROMPT


def get_input(messages: list[OpenAICompatibleMessage]):
    return "\n".join([f"[{m.role}]: {m.content}" for m in messages])


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
