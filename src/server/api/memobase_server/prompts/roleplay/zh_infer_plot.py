import re
from ...env import CONFIG
from ...models.blob import OpenAICompatibleMessage

ADD_KWARGS = {
    "prompt_id": "roleplay.zh_infer_plot",
}
INFER_PLOT_PROMPT = """你是一个专业的编剧，你的任务是顺延User和Assistant的对话设计新的剧情，让用户可以有新的，感兴趣的剧情体验

## 输入格式
- Assistant的背景放在<assistant_role_setting>标签中
- User的背景放在<user_role_setting>标签中
- 之前的已经尝试过故事剧情放在<before_plots>标签中，你需要注意不要重复之前的剧情
- 最新的对话放在<latest_dialogues>标签中

## 输出新剧情
你需要着重参考latest_dialogues中的对话，设计新的剧情。
你也可以参考部分Assistant和User的背景设定，但请注意不要重复之前的剧情
### 输出格式
```xml
<themes>
...
</themes>
<overview>
....
</overview>
<timeline>
1. ...
2. ...
...
</timeline>
```
- 在themes中，你需要选定接下来剧情的一些基调（e.g. 爱情, 科幻, 悬疑, 奇幻 ...）, 请注意，你选取的基调不能和用户当前对话偏离过远，如果对话中没有明显的基调，则需要参考user和assistant的背景设定。
- 在overview中，你需要用1-2句话描述新剧情的发展概要
- 在timeline中，你需要描述新剧情的具体剧情安排，一步步从最新对话的状态过渡到你设计的剧情当中，用orderlist的格式输出，每一步剧情简单描述即可，不需要涉及到具体的对话设计，只是剧情框架。 控制在5-10步

你输出的剧情要满足如下的要求：
- 不能跳跃：剧情第一步要从当前的对话开始往后延续
- 不能老套：不要只专注于背景设定，要从设定中挖掘出新的剧情
- 创造冲突：利用Potogonist Vs Antogonist，unbreakable bonding等方法为后续剧情创作冲突
- 创造剧情张力： 利用隐藏剧情,时间限制，转折点等方法为后续剧情创作张力
- 时间线要有起承转合
新剧情以用户的第一视角进行撰写，围绕“我”(User)和“你”(Assistant)展开

现在，请开始你的任务
"""


def get_prompt() -> str:
    return INFER_PLOT_PROMPT


def pack_messages(messages: list[OpenAICompatibleMessage]):
    return "\n".join(
        [
            f"[{m.role}{f'({m.alias})' if m.alias else ''}]: {m.content}"
            for m in messages
        ]
    )


def get_input(role, user, before_plots: list[str], messages: list):
    return f"""<assistant_role_setting>
{role}
</assistant_role_setting>
<user_role_setting>
{user}
</user_role_setting>
<before_plots>
{before_plots}
</before_plots>
<latest_dialogues>
{pack_messages(messages)}
</latest_dialogues>"""


def get_kwargs() -> dict:
    return ADD_KWARGS


def extract_plot_output(content: str):
    overview = re.search(r"<overview>(.*?)</overview>", content, re.DOTALL)
    themes = re.search(r"<themes>(.*?)</themes>", content, re.DOTALL)
    timeline = re.search(r"<timeline>(.*?)</timeline>", content, re.DOTALL)
    return overview.group(1), themes.group(1), timeline.group(1)


if __name__ == "__main__":
    print(get_prompt())
