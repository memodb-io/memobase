from ..env import CONFIG, LOG
from .profile_init_utils import (
    UserProfileTopic,
    formate_profile_topic,
    modify_default_user_profile,
)


CANDIDATE_PROFILE_TOPICS: list[UserProfileTopic] = [
    UserProfileTopic(
        "基本情報",
        sub_topics=[
            "氏名",
            {
                "name": "年齢",
                "description": "整数",
            },
            "性別",
            "生年月日",
            "国籍",
            "民族",
            "使用言語",
        ],
    ),
    UserProfileTopic(
        "連絡先",
        sub_topics=[
            "電子メール",
            "電話",
            "市区町村",
            "都道府県",
            "国",
        ],
    ),
    UserProfileTopic(
        "学歴",
        sub_topics=[
            "出身校",
            "学位",
            "専攻",
            "卒業年",
        ],
    ),
    UserProfileTopic(
        "人口統計",
        sub_topics=[
            "婚姻状況",
            "子供の数",
            "世帯収入",
        ],
    ),
    UserProfileTopic(
        "仕事",
        sub_topics=[
            "会社",
            "役職",
            "業界",
            "以前のプロジェクト",
            "スキル",
        ],
    ),
    UserProfileTopic(
        "興味",
        sub_topics=[
            "本",
            "映画",
            "音楽",
            "料理",
            "運動",
        ],
    ),
    UserProfileTopic(
        "ライフスタイル",
        sub_topics=[
            {"name": "食事の好み", "description": "例: ベジタリアン、ヴィーガン"},
            "運動習慣",
            "健康状態",
            "睡眠パターン",
            "喫煙",
            "飲酒",
        ],
    ),
    UserProfileTopic(
        "心理的特性",
        sub_topics=["性格", "価値観", "信念", "動機", "目標"],
    ),
    UserProfileTopic(
        "ライフイベント",
        sub_topics=["結婚", "引っ越し", "退職"],
    ),
]


CANDIDATE_PROFILE_TOPICS = modify_default_user_profile(CANDIDATE_PROFILE_TOPICS)


def get_prompt(profiles: list[UserProfileTopic] = CANDIDATE_PROFILE_TOPICS):
    return "\n".join([formate_profile_topic(up) for up in profiles]) + "\n..."


if CONFIG.language == "ja":
    LOG.info(f"User profiles: \n{get_prompt()}")

if __name__ == "__main__":
    from .profile_init_utils import export_user_profile_to_yaml

    # print(get_prompt())
    print(export_user_profile_to_yaml(CANDIDATE_PROFILE_TOPICS))
