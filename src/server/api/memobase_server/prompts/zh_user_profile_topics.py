from ..env import CONFIG, LOG
from .types import UserProfileTopic


CANDIDATE_PROFILE_TOPICS: list[UserProfileTopic] = [
    UserProfileTopic(
        "基本信息",
        [
            "用户姓名",
            {
                "name": "用户年龄",
                "description": "整数",
            },
            "性别",
            "出生日期",
            "国籍",
            "民族",
            "语言",
        ],
    ),
    UserProfileTopic(
        "联系信息",
        [
            "电子邮件",
            "电话",
            "地址",
            "城市",
            "省份",
            "国家",
            "邮政编码",
        ],
    ),
    UserProfileTopic(
        "教育背景",
        [
            "学校",
            "学位",
            "专业",
            "毕业年份",
            "研究领域",
            "教育机构",
        ],
    ),
    UserProfileTopic(
        "人口统计",
        [
            "婚姻状况",
            "子女数量",
            "家庭收入",
        ],
    ),
    UserProfileTopic(
        "工作",
        [
            "公司",
            "职位",
            "工作地点",
            "入职日期",
            "离职日期",
            "所属行业",
            "参与项目",
            "工作技能",
        ],
    ),
    UserProfileTopic(
        "兴趣爱好",
        [
            "书籍",
            "喜欢的作者",
            "电影",
            "电视节目",
            "音乐",
            "音乐类型",
            "美食",
            "运动",
            "户外活动",
            "游戏",
            "座右铭",
        ],
    ),
    UserProfileTopic(
        "生活方式",
        [
            {"name": "饮食偏好", "description": "例如：素食，纯素"},
            "运动习惯",
            "健康状况",
            "睡眠模式",
            "吸烟",
            "饮酒",
        ],
    ),
    UserProfileTopic(
        "心理特征",
        ["性格特点", "价值观", "信仰", "动力", "目标"],
    ),
    UserProfileTopic(
        "人生大事",
        ["婚姻", "搬迁", "退休"],
    ),
]


if CONFIG.overwrite_user_profiles is not None:
    CANDIDATE_PROFILE_TOPICS = [
        UserProfileTopic(up["topic"], up["sub_topics"])
        for up in CONFIG.overwrite_user_profiles
    ]
elif CONFIG.additional_user_profiles:
    _addon_user_profiles = [
        UserProfileTopic(up["topic"], up["sub_topics"])
        for up in CONFIG.additional_user_profiles
    ]
    CANDIDATE_PROFILE_TOPICS.extend(_addon_user_profiles)
if CONFIG.language == "zh":
    LOG.info(f"User profiles: {CANDIDATE_PROFILE_TOPICS}")


def formate_profile_topic(topic: UserProfileTopic) -> str:
    if not topic.sub_topics:
        return f"- {topic.topic}"
    return f"- {topic.topic}. 包括sub_topics: " + ", ".join(
        [
            f"{sp['name']}"
            + (f"({sp['description']})" if sp.get("description") else "")
            for sp in topic.sub_topics
        ]
    )


def get_prompt():
    return (
        "\n".join([formate_profile_topic(up) for up in CANDIDATE_PROFILE_TOPICS])
        + "\n..."
    )


if __name__ == "__main__":
    print(get_prompt())
