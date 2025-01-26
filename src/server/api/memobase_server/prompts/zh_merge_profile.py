from .utils import pack_merge_action_into_string
from ..env import CONFIG

ADD_KWARGS = {}
EXAMPLES = [
    {
        "input": """## 用户主题
基本信息, 年龄
## 旧备忘录
用户39岁
## 新备忘录
用户40岁
""",
        "response": {
            "action": "UPDATE",
            "memo": "用户40岁",
        },
    },
    {
        "input": """## 用户主题
个性, 情绪反应
## 旧备忘录
下雨天用户有时会哭泣
## 新备忘录
下雨天用户会想起了家乡
""",
        "response": {
            "action": "UPDATE",
            "memo": "下雨天用户会想起家乡，可能是其下雨天哭泣的原因之一",
        },
    },
    {
        "input": """## 用户主题
基本信息, 生日
## 旧备忘录
1999/04/30
## 新备忘录
用户没有提及生日
""",
        "response": {
            "action": "UPDATE",
            "memo": "1999/04/30",
        },
    },
]

MERGE_FACTS_PROMPT = """你是一个智能备忘录管理器，负责控制用户的记忆/形象。
你将收到两条关于用户同一主题/方面的备忘录，一条是旧的，一条是新的。
你应更新旧的备忘录，以包含新的备忘录中的信息。
并以输出格式返回你的结果：
- UPDATE{tab}MEMO
以'- '开头，接下来是'UPDATE'，然后是'{tab}'，最后是最终的MEMO备忘录(5句话以内)。

以下是如何生成最终的备忘录的指导原则：
## 替换旧备忘录
如果新备忘录与旧备忘录完全冲突，你应该用新的备忘录替换旧的备忘录。
**示例**：
{example_replace}

## 合并备忘录
如果旧备忘录中包含新备忘录中没有的信息，你应该将旧备忘录和新备忘录合并。
你需要总结新旧备忘录的内容，以便在最终备忘录中包含充分的信息。
**示例**：
{example_merge}

## 保持旧备忘录
如果新备忘录中没有新的信息或者不包含任何有效信息，你应该保持旧的备忘录不变。
**示例**：
{example_keep}


理解备忘录，你可以从新备忘录和旧备忘录中推断信息以决定正确的操作。
遵循以下说明：
- 不要返回上面提供的自定义少量提示中的任何内容。
- 严格遵守正确的格式。
- 最终的备忘录不能超过5句话, 不能超过100个字
- 保持备忘录的简洁性
"""


def get_input(topic, subtopic, old_memo, new_memo):
    return f"""
## 用户主题
{topic}, {subtopic}
## 旧备忘录
{old_memo}
## 新备忘录
{new_memo}
"""


def get_prompt() -> str:
    example_add = f"""INPUT:
{EXAMPLES[0]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[0]['response'])}
"""
    example_update = f"""INPUT:
{EXAMPLES[1]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[1]['response'])}
"""
    example_keep = f"""INPUT:
{EXAMPLES[2]['input']}
OUTPUT:
{pack_merge_action_into_string(EXAMPLES[2]['response'])}
"""
    return MERGE_FACTS_PROMPT.format(
        example_replace=example_add,
        example_merge=example_update,
        example_keep=example_keep,
        tab=CONFIG.llm_tab_separator,
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
