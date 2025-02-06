from ..env import CONFIG, LOG
from .types import UserProfileTopic, formate_profile_topic, modify_default_user_profile


CANDIDATE_PROFILE_TOPICS: list[UserProfileTopic] = [
    UserProfileTopic(
        "基本信息",
        sub_topics=[
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
        sub_topics=[
            "电子邮件",
            "电话",
            "城市",
            "省份",
        ],
    ),
    UserProfileTopic(
        "教育背景",
        sub_topics=[
            "学校",
            "学位",
            "专业",
            "毕业年份",
        ],
    ),
    UserProfileTopic(
        "人口统计",
        sub_topics=[
            "婚姻状况",
            "子女数量",
            "家庭收入",
        ],
    ),
    UserProfileTopic(
        "工作",
        sub_topics=[
            "公司",
            "职位",
            "工作地点",
            "参与项目",
            "工作技能",
        ],
    ),
    UserProfileTopic(
        "兴趣爱好",
        sub_topics=[
            "书籍",
            "电影",
            "音乐",
            "美食",
            "运动",
        ],
    ),
    UserProfileTopic(
        "生活方式",
        sub_topics=[
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
        sub_topics=["性格特点", "价值观", "信仰", "动力", "目标"],
    ),
    UserProfileTopic(
        "人生大事",
        sub_topics=["婚姻", "搬迁", "退休"],
    ),
]


CANDIDATE_PROFILE_TOPICS = modify_default_user_profile(CANDIDATE_PROFILE_TOPICS)


def get_prompt(profiles: list[UserProfileTopic] = CANDIDATE_PROFILE_TOPICS):
    return "\n".join([formate_profile_topic(up) for up in profiles]) + "\n..."


if CONFIG.language == "zh":
    LOG.info(f"User profiles: \n{get_prompt()}")

if __name__ == "__main__":
    from .types import export_user_profile_to_yaml

    # print(get_prompt())
    print(export_user_profile_to_yaml(CANDIDATE_PROFILE_TOPICS))
