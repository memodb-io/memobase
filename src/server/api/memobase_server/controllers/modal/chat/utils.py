from typing import TypedDict
from ....env import CONFIG
from ....models.response import UserProfilesData
from ...project import ProfileConfig
from ....prompts.profile_init_utils import read_out_profile_config
from .types import PROMPTS
from ....types import UserProfileTopic
from ....env import ContanstTable
from ....utils import truncate_string
from ....prompts.utils import attribute_unify


class PackCurrentUserProfilesResult(TypedDict):
    already_topics_prompt: str
    allowed_topic_subtopics: set[tuple[str, str]]
    already_topic_subtopics_values: dict[tuple[str, str], str]
    project_profile_slots: list[UserProfileTopic]
    use_language: str
    strict_mode: bool


def pack_current_user_profiles(
    current_user_profiles: UserProfilesData, project_profiles: ProfileConfig
) -> PackCurrentUserProfilesResult:
    profiles = current_user_profiles.profiles
    USE_LANGUAGE = project_profiles.language or CONFIG.language
    STRICT_MODE = (
        project_profiles.profile_strict_mode
        if project_profiles.profile_strict_mode is not None
        else CONFIG.profile_strict_mode
    )

    project_profiles_slots = read_out_profile_config(
        project_profiles, PROMPTS[USE_LANGUAGE]["profile"].CANDIDATE_PROFILE_TOPICS
    )
    if STRICT_MODE:
        allowed_topic_subtopics = set()
        for p in project_profiles_slots:
            for st in p.sub_topics:
                allowed_topic_subtopics.add(
                    (attribute_unify(p.topic), attribute_unify(st["name"]))
                )
    else:
        allowed_topic_subtopics = None

    if len(profiles):
        already_topics_subtopics = set(
            [
                (
                    attribute_unify(p.attributes[ContanstTable.topic]),
                    attribute_unify(p.attributes[ContanstTable.sub_topic]),
                )
                for p in profiles
            ]
        )
        already_topic_subtopics_values = {
            (
                attribute_unify(p.attributes[ContanstTable.topic]),
                attribute_unify(p.attributes[ContanstTable.sub_topic]),
            ): p.content
            for p in profiles
        }
        if STRICT_MODE:
            already_topics_subtopics = already_topics_subtopics.intersection(
                allowed_topic_subtopics
            )
            already_topic_subtopics_values = {
                k: already_topic_subtopics_values[k] for k in already_topics_subtopics
            }
        already_topics_subtopics = sorted(already_topics_subtopics)
        already_topics_prompt = "\n".join(
            [
                f"- {topic}{CONFIG.llm_tab_separator}{sub_topic}{CONFIG.llm_tab_separator}{truncate_string(already_topic_subtopics_values[(topic, sub_topic)], 5)}"
                for topic, sub_topic in already_topics_subtopics
            ]
        )
    else:
        already_topics_prompt = ""
        already_topic_subtopics_values = {}

    return {
        "already_topics_prompt": already_topics_prompt,
        "allowed_topic_subtopics": allowed_topic_subtopics,
        "already_topic_subtopics_values": already_topic_subtopics_values,
        "project_profile_slots": project_profiles_slots,
        "use_language": USE_LANGUAGE,
        "strict_mode": STRICT_MODE,
    }
