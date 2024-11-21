from datetime import datetime, timedelta
from . import zh_user_profile_topics

EXAMPLES = [
    (
        """
<chat data_index=0>
    user: 你好，今天过得怎么样？
</chat>
""",
        {"facts": []},
    ),
    (
        """
<chat data_index=0>
    user: 我还是不敢相信我们今天结婚了！
    assistant: 我知道，这将是我人生中最美好的旅程。
</chat>
""",
        {
            "facts": [
                {
                    "topic": "人口统计",
                    "sub_topic": "婚姻状况",
                    "memo": "用户与assistant已婚, 结婚日期在$$TODAY$$",
                    "cites": [0],
                }
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: 你好，我住在旧金山，想找一家日常餐厅。
</chat>
""",
        {
            "facts": [
                {
                    "topic": "联系方式",
                    "sub_topic": "城市",
                    "memo": "旧金山",
                    "cites": [0],
                }
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: 你能给我写一封博士申请推荐信吗？
    assistant: 明白了，Melinda！...
    user: 谢谢你记得我的名字！
</chat>
""",
        {
            "facts": [
                {
                    "topic": "基本信息",
                    "sub_topic": "可能的姓名",
                    "memo": "用户被称为Melinda",
                    "cites": [0],
                },
                {
                    "topic": "教育经历",
                    "sub_topic": "学历",
                    "memo": "用户在$$TODAY$$正在申请博士学位",
                    "cites": [0],
                },
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: 昨天下午3点我和John开了个会，讨论了新项目。
</chat>
""",
        {
            "facts": [
                {
                    "topic": "工作",
                    "sub_topic": "合作",
                    "memo": "用户正在与John开始一个项目，已经在$$YESTERDAY$$见过一次面",
                    "cites": [0],
                }
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: 你好，我叫John，我是MemoBase的软件工程师。
</chat>
""",
        {
            "facts": [
                {
                    "topic": "基本信息",
                    "sub_topic": "姓名",
                    "memo": "John",
                    "cites": [0],
                },
                {
                    "topic": "工作",
                    "sub_topic": "职位",
                    "memo": "用户是软件工程师",
                    "cites": [0],
                },
                {
                    "topic": "工作",
                    "sub_topic": "公司",
                    "memo": "用户在MemoBase工作",
                    "cites": [0],
                },
            ]
        },
    ),
    (
        """
<chat data_index=0>
    user: 我最喜欢的电影是《盗梦空间》和《星际穿越》。
    assistant: 这些都是很棒的电影，你看过《信条》吗？
</chat>
<chat data_index=1>
    user: 我看过《信条》，事实上那是我最喜欢的。
</chat>
""",
        {
            "facts": [
                {
                    "topic": "兴趣爱好",
                    "sub_topic": "电影",
                    "memo": "《盗梦空间》、《星际穿越》和《信条》；最喜欢的是《信条》",
                    "cites": [0, 1],
                },
                {
                    "topic": "兴趣爱好",
                    "sub_topic": "电影导演",
                    "memo": "用户似乎是克里斯托弗·诺兰的忠实粉丝",
                    "cites": [1],
                },
            ]
        },
    ),
]

FACT_RETRIEVAL_PROMPT = """你是一位专业的心理学家。
你的责任是仔细阅读用户与其他方的对话。然后提取相关且重要的事实、用户偏好，这些信息将有助于评估用户的状态。
你不仅要提取明确陈述的信息，还要推断对话中隐含的信息。
请注意， 你要准确的提取和推断用户相关(user)的信息，而非其他方(assistant)的


## 你应该关注的主题
以下是一些可以参考的主题/子主题示例：
{user_profile_topics}
如果你认为有必要，可以创建自己的主题/子主题，任何有助于评估用户状态的信息都是受欢迎的。


## 引用来源
对于每条信息，你都应该引用信息共享时的对话索引 `data_index`。
请注意为每条信息引用正确的 `data_index`，这将有助于你以后更好地理解用户。

## 格式要求
### 输出
你需要从对话中提取事实和偏好，并将它们放在"facts"字段的列表中：
{{
    "facts": [
        {{
            "topic": "基本信息",
            "sub_topic": "姓名", # 如果有子主题的话，否则输出空字符串 ""
            "memo": "小明",
            "cites": [data_index_i, data_index_j,....]
        }}
    ]
}}
"facts"字段中的每个元素都是一个字典，包含：
- "topic": 该元素关注的主题/类别，字符串。
- "sub_topic": 该元素关注的详细主题/类别，字符串，可选，无子主题时输出 ""。
- "memo": 提取的关于`用户`的信息、事实或偏好，字符串。
- "cites": 信息共享时的data_index列表，整数列表。
  data_index在对话的XML属性中给出。


## 示例
以下是一些示例：
{examples}

请按上述json格式返回事实和偏好。

请记住以下几点：
- 今天是 {today}。
- 如果在以下对话中没有找到任何相关信息，可以返回空列表。
- 确保按照格式和示例部分中提到的格式返回响应。
- 对于提取的每个事实/偏好，确保引用信息共享时的正确且相关的data_index。
- 你应该推断对话中隐含的内容，而不仅仅是明确陈述的内容。
- 相同的内容不需要在不同的topic和sub_topic下重复, 选择最相关的主题和子主题即可。
- 相同的topic和sub_topic只能出现一次


## 用户之前的主题
以下是用户已经与助手分享的主题和子主题：
{before_topics}
如果对话中再次提到相同的主题/子主题，请考虑使用相同的主题/子主题。

以下是用户和助手之间的对话。你需要从对话中提取/推断相关的事实和偏好，并按上述json格式返回。
请注意， 你要准确的提取和推断用户相关(user)的信息，而非其他方(assistant)的
你应该检测用户输入的语言，并用相同的语言记录事实。
如果在以下对话中没有找到任何相关事实、用户记忆和偏好，你可以在"facts"键对应的位置返回空列表。
"""


def get_prompt(already_topics: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    examples = "\n\n".join([f"Input: {p[0]}Output: {p[1]}" for p in EXAMPLES])
    examples = examples.replace("$$TODAY$$", today).replace("$$YESTERDAY$$", yesterday)
    return FACT_RETRIEVAL_PROMPT.format(
        before_topics=already_topics,
        today=today,
        examples=examples,
        user_profile_topics=zh_user_profile_topics.get_prompt(),
    )


if __name__ == "__main__":
    print(get_prompt(already_topics=""))
