from dataclasses import dataclass, field
from typing import TypedDict, Optional

from ..env import CONFIG, LOG

SubTopic = TypedDict("SubTopic", {"name": str, "description": Optional[str]})


@dataclass
class UserProfileTopic:
    topic: str
    description: Optional[str] = None
    sub_topics: list[SubTopic] = field(default_factory=list)

    def __post_init__(self):
        self.sub_topics = [
            {"name": st, "description": None} if isinstance(st, str) else st
            for st in self.sub_topics
        ]
        for st in self.sub_topics:
            assert isinstance(st["name"], str)
            assert isinstance(st["description"], (str, type(None)))


def formate_profile_topic(topic: UserProfileTopic) -> str:
    if not topic.sub_topics:
        return f"- {topic.topic}"
    return f"- {topic.topic} ({topic.description or ''})\n    - " + "\n    - ".join(
        [
            f"{sp['name']}"
            + (f"({sp['description']})" if sp.get("description") else "")
            for sp in topic.sub_topics
        ]
    )


def modify_default_user_profile(CANDIDATE_PROFILE_TOPICS):
    if CONFIG.overwrite_user_profiles is not None:
        CANDIDATE_PROFILE_TOPICS = [
            UserProfileTopic(
                up["topic"],
                description=up.get("description", None),
                sub_topics=up["sub_topics"],
            )
            for up in CONFIG.overwrite_user_profiles
        ]
    elif CONFIG.additional_user_profiles:
        _addon_user_profiles = [
            UserProfileTopic(
                up["topic"],
                description=up.get("description", None),
                sub_topics=up["sub_topics"],
            )
            for up in CONFIG.additional_user_profiles
        ]
        CANDIDATE_PROFILE_TOPICS.extend(_addon_user_profiles)
    return CANDIDATE_PROFILE_TOPICS