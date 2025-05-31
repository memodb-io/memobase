from ....env import ContanstTable, CONFIG, LOG
from ...status import append_user_status, get_user_statuses
from ...profile import get_user_profiles, truncate_profiles
from ...project import get_project_profile_config
from ....models.blob import OpenAICompatibleMessage
from ....models.utils import Promise
from ....models.response import ProactiveTopicData
from ...profile import get_user_profiles, truncate_profiles
from .detect_interest import detect_chat_interest
from .predict_new_topics import predict_new_topics

# from .types import


def pack_timeline_prompt(timeline: str, language: str) -> str:
    if language == "zh":
        return f"## 下面是你的剧本，如果我没有主动提供话题的话，参考下面剧情推动我们的对话：\n{timeline}##"
    else:
        return f"## Here is your script, if I don't provide a topic, please refer to the following plot to drive our conversation: \n{timeline}##"


async def process_messages(
    user_id: str,
    project_id: str,
    messages: list[OpenAICompatibleMessage],
    agent_context: str = None,
    prefer_topics: list[str] = None,
    topk: int = None,
    max_token_size: int = None,
    only_topics: list[str] = None,
    max_subtopic_size: int = None,
    topic_limits: dict[str, int] = None,
) -> Promise[ProactiveTopicData]:
    p = await get_project_profile_config(project_id)
    if not p.ok():
        return p
    project_profiles = p.data()
    USE_LANGUAGE = "zh"
    # USE_LANGUAGE = project_profiles.language or CONFIG.language

    interest = await detect_chat_interest(
        project_id,
        messages,
        profile_config=project_profiles,
    )
    if not interest.ok():
        return interest
    interest_data = interest.data()
    if interest_data["action"] != "new_topic":
        await append_user_status(
            user_id,
            project_id,
            ContanstTable.roleplay_plot_status,
            {
                "interest": interest_data,
            },
        )
        return Promise.resolve(ProactiveTopicData(action="continue"))
    latests_statuses = await get_user_statuses(
        user_id, project_id, type=ContanstTable.roleplay_plot_status
    )
    if not latests_statuses.ok():
        return latests_statuses
    latests_statuses_data = latests_statuses.data()

    p = await get_user_profiles(user_id, project_id)
    if not p.ok():
        return p
    p = await truncate_profiles(
        p.data(),
        prefer_topics=prefer_topics,
        topk=topk,
        max_token_size=max_token_size,
        only_topics=only_topics,
        max_subtopic_size=max_subtopic_size,
        topic_limits=topic_limits,
    )
    if not p.ok():
        return p
    user_profiles_data = p.data()
    use_user_profiles = user_profiles_data.profiles
    user_context = "\n".join(
        [
            f"{p.attributes.get('topic')}::{p.attributes.get('sub_topic')}: {p.content}"
            for p in use_user_profiles
        ]
    )

    p = await predict_new_topics(
        project_id,
        messages,
        latests_statuses_data,
        user_context,
        agent_context,
        project_profiles,
    )
    if not p.ok():
        return p
    plot = p.data()
    await append_user_status(
        user_id,
        project_id,
        ContanstTable.roleplay_plot_status,
        {
            "interest": interest_data,
            "new_topic": plot,
            "chats": [m.model_dump() for m in messages],
        },
    )

    return Promise.resolve(
        ProactiveTopicData(
            action="new_topic",
            topic_prompt=pack_timeline_prompt(plot["timeline"], USE_LANGUAGE),
        )
    )
