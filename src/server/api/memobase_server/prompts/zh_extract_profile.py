from . import zh_user_profile_topics
from ..models.response import AIUserProfiles
from ..env import CONFIG, LOG
from .utils import pack_profiles_into_string

ADD_KWARGS = {
    "prompt_id": "zh_extract_profile",
}

EXAMPLES = [
    (
        """
[2025/01/01] user: 你好，今天过得怎么样？
""",
        AIUserProfiles(**{"facts": []}),
    ),
    (
        """
[2025/01/01] user: 小姨你好呀， 我现在在北京
[2025/01/01] assistant: 哦，你最近来北京了，是吗？
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "基本信息",
                        "sub_topic": "居住地",
                        "memo": "北京",
                    }
                ]
            }
        ),
    ),
    (
        """
[2025/01/01] user: 我还是不敢相信我们今天结婚了！
[2025/01/01] Silei: 我知道，这将是我人生中最美好的旅程。
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "人口统计",
                        "sub_topic": "婚姻状况",
                        "memo": "用户与Silei已婚, 结婚日期在2025/01/01",
                    }
                ]
            }
        ),
    ),
    (
        """
[2025/01/4] user: 你好，我住在旧金山，想找一家日常餐厅。
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "联系方式",
                        "sub_topic": "城市",
                        "memo": "旧金山",
                    }
                ]
            }
        ),
    ),
    (
        """
[2025/01/14] user: 你能给我写一封博士申请推荐信吗？
[2025/01/14] assistant: 明白了，Melinda！...
[2025/01/14] user: 谢谢你记得我的名字！
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "基本信息",
                        "sub_topic": "姓名",
                        "memo": "用户被称为Melinda",
                    },
                    {
                        "topic": "教育经历",
                        "sub_topic": "学历",
                        "memo": "用户在2025/01/14正在申请博士学位",
                    },
                ]
            }
        ),
    ),
    (
        """
[2024/10/12] user: 昨天下午3点我和John开了个会，讨论了新项目。
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "工作",
                        "sub_topic": "合作",
                        "memo": "用户正在与John开始一个新项目，已经在2024/10/11见过一次面",
                    }
                ]
            }
        ),
    ),
    (
        """
[2025/01/14] user: 你好，我叫John，我是MemoBase的软件工程师。
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "基本信息",
                        "sub_topic": "姓名",
                        "memo": "John",
                    },
                    {
                        "topic": "工作",
                        "sub_topic": "职位",
                        "memo": "用户是软件工程师",
                    },
                    {
                        "topic": "工作",
                        "sub_topic": "公司",
                        "memo": "用户在MemoBase工作",
                    },
                ]
            }
        ),
    ),
    (
        """
[2025/01/14] user: 我最喜欢的电影是《盗梦空间》和《星际穿越》。
[2025/01/14] assistant: 这些都是很棒的电影，你看过《信条》吗？
[2025/01/14] user: 我看过《信条》，事实上那是我最喜欢的。
""",
        AIUserProfiles(
            **{
                "facts": [
                    {
                        "topic": "兴趣爱好",
                        "sub_topic": "电影",
                        "memo": "《盗梦空间》、《星际穿越》和《信条》；最喜欢的是《信条》",
                    },
                    {
                        "topic": "兴趣爱好",
                        "sub_topic": "电影导演",
                        "memo": "用户似乎是克里斯托弗·诺兰的忠实粉丝",
                    },
                ]
            }
        ),
    ),
]

DEFAULT_JOB = """你是一位专业的心理学家。
你的责任是仔细阅读用户与其他方的对话。然后提取相关且重要的事实、用户偏好，这些信息将有助于评估用户的状态。
你不仅要提取明确陈述的信息，还要推断对话中隐含的信息。
请注意，你要准确地提取和推断用户相关(user)的信息，而非其他方(assistant)的。
"""

FACT_RETRIEVAL_PROMPT = """{system_prompt}

## 格式
### 输入
#### 主题建议
这个章节里会放一些主题和子主题的建议，你需要参考这些主题和子主题来提取信息。
如果你认为有必要，可以创建自己的主题/子主题，任何有助于评估用户状态的信息都是受欢迎的。
#### 已有的主题
这个章节中会放用户已经与助手分享的主题和子主题
如果对话中再次提到相同的主题/子主题，请考虑使用相同的主题/子主题。
#### 对话
输入的格式是用户和另一方的对话:
- [TIME] NAME: MESSAGE
其中NAME有时候是user，有时候是assistant。
MESSGAE则是对话内容. 理解对话内容并且记住事情发生的时间

### 输出
你需要从对话中提取事实和偏好，并按顺序列出：
- TOPIC{tab}SUB_TOPIC{tab}MEMO
例如：
- 基本信息{tab}姓名{tab}melinda
- 工作{tab}职称{tab}软件工程师

每行代表一个事实或偏好，包含：
1. TOPIC: 主题，表示该偏好的类别
2. SUB_TOPIC: 详细主题，表示该偏好的具体类别
3. MEMO: 提取的信息、事实或偏好
这些元素应以 `{tab}` 分隔，每行应以 `\n` 分隔，并以 "- " 开头。


## 示例
以下是一些示例：
{examples}

请按上述格式返回事实和偏好。

请记住以下几点：
- 如果用户有提到时间敏感的信息，试图推理出具体的日期.
- 当可能时，请使用具体日期，而不是使用“今天”或“昨天”等相对时间。
- 如果在以下对话中没有找到任何相关信息，可以返回空列表。
- 确保按照格式和示例部分中提到的格式返回响应。
- 你应该推断对话中隐含的内容，而不仅仅是明确陈述的内容。
- 相同的内容不需要在不同的 topic 和 sub_topic 下重复，选择最相关的主题和子主题即可。
- 相同的 topic 和 sub_topic 只能出现一次。
忽视用户(user)对其他方(assistant)的称呼：比如用户称呼其他方(assistant)为小姨，因为对其他方的称呼不一定代表真实的关系，不需要推断用户有一个小姨， 只需要记录用户称呼其他方为小姨即可


以下是用户和助手之间的对话。你需要从对话中提取/推断相关的事实和偏好，并按上述格式返回。
请注意，你要准确地提取和推断用户相关(user)的信息，而非其他方(assistant)的。
你应该检测用户输入的语言，并用相同的语言记录事实。
如果在以下对话中没有找到任何相关事实、用户记忆和偏好，你可以返回"NONE"或"NO FACTS"。
"""


def pack_input(already_input, chat_strs, topic_examples):
    return f"""#### 主题建议
{topic_examples}
#### 已有的主题
{already_input}
#### 对话
{chat_strs}
"""


def get_default_profiles() -> str:
    return zh_user_profile_topics.get_prompt()


def get_prompt() -> str:
    sys_prompt = CONFIG.system_prompt or DEFAULT_JOB
    examples = "\n\n".join(
        [f"Input: {p[0]}Output:\n{pack_profiles_into_string(p[1])}" for p in EXAMPLES]
    )
    return FACT_RETRIEVAL_PROMPT.format(
        system_prompt=sys_prompt, examples=examples, tab=CONFIG.llm_tab_separator
    )


def get_kwargs() -> dict:
    return ADD_KWARGS


if __name__ == "__main__":
    print(get_prompt())
