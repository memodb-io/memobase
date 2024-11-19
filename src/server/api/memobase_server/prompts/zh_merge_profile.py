from datetime import datetime

EXAMPLES = [
    {
        "input": """## User Topic
基本信息, 年龄

## Old Memo
用户39岁
## New Memo
用户40岁
""",
        "response": {
            "action": "REPLACE",
            "memo": "用户40岁",
        },
    },
    {
        "input": """## User Topic
个性, 情绪反应

## Old Memo
下雨天用户有时会哭泣
## New Memo
下雨天用户会想起了家乡而心情低落
""",
        "response": {
            "action": "MERGE",
            "memo": "下雨天用户会想起家乡从而心情低落，可能是其下雨天哭泣的原因之一",
        },
    },
]

MERGE_FACTS_PROMPT = """你是一个智能备忘录管理器，负责控制用户的记忆/形象。
你将收到两条关于用户同一主题/方面的memo，一条是旧的，一条是新的。
你的决策空间如下：
(1) REPLACE：用new memo替换old memo
(2) MERGE：将old memo与new memo合并
将你的操作放在'action'字段中，最终的备忘录放在'memo'字段中。
并以JSON格式返回你的结果。

将新获取的事实与现有记忆进行比较。对于每个新事实，决定是否：
- REPLACE：new memo与old memo完全相冲突，那么输出"REPLACE"到'action'，让old memo被new memo替换。
- MERGE：new memo和old memo讲述了同一个故事的不同部分或者旧备忘录只有部分冲突和过时的地方，输出"REPLACE"到'action'，然后你需要结合old memo和new memo重新总结一个新的memo。

以下是选择执行哪种操作的具体指导原则：

## REPLACE
**示例**：
{example_replace}

## MERGE
**示例**：
{example_merge}

智慧地理解备忘录，你可以从new memo和old memo中推断信息以决定正确的操作。
遵循以下说明：
- 不要返回上面提供的自定义少量提示中的任何内容。
- 严格遵守正确的JSON格式。

除了JSON格式外，不要返回任何其他内容。
"""


def get_input(topic, subtopic, old_memo, new_memo):
    return f"""
## User Topic
{topic}, {subtopic}
## Old Memo
{old_memo}
## New Memo
{new_memo}
"""


def get_prompt() -> str:
    example_add = f"""INPUT:
{EXAMPLES[0]['input']}
OUTPUT:
{EXAMPLES[0]['response']}
"""
    example_update = f"""INPUT:
{EXAMPLES[1]['input']}
OUTPUT:
{EXAMPLES[1]['response']}
"""
    return MERGE_FACTS_PROMPT.format(
        example_replace=example_add, example_merge=example_update
    )


if __name__ == "__main__":
    print(get_prompt())
