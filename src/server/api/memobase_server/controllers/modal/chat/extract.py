from ....env import CONFIG, ContanstTable, TRACE_LOG
from ....models.utils import Promise
from ....models.response import AIUserProfiles, CODE, UserProfilesData
from ....llms import llm_complete
from ....prompts.utils import (
    attribute_unify,
    parse_string_into_profiles,
)
from ....prompts.profile_init_utils import read_out_profile_config, UserProfileTopic
from ...project import ProfileConfig
from .types import FactResponse, PROMPTS
from .utils import pack_current_user_profiles


def merge_by_topic_sub_topics(new_facts: list[FactResponse]):
    topic_subtopic = {}
    for nf in new_facts:
        key = (nf[ContanstTable.topic], nf[ContanstTable.sub_topic])
        if key in topic_subtopic and isinstance(nf["memo"], str):
            topic_subtopic[key]["memo"] += f"; {nf['memo']}"
            continue
        topic_subtopic[key] = nf
    return list(topic_subtopic.values())


async def extract_topics(
    user_id: str,
    project_id: str,
    user_memo: str,
    project_profiles: ProfileConfig,
    current_user_profiles: UserProfilesData,
) -> Promise[dict]:

    profiles = current_user_profiles.profiles
    CURRENT_PROFILE_INFO = pack_current_user_profiles(
        current_user_profiles, project_profiles
    )
    USE_LANGUAGE = CURRENT_PROFILE_INFO["use_language"]
    STRICT_MODE = CURRENT_PROFILE_INFO["strict_mode"]

    project_profiles_slots = CURRENT_PROFILE_INFO["project_profile_slots"]

    p = await llm_complete(
        project_id,
        PROMPTS[USE_LANGUAGE]["extract"].pack_input(
            CURRENT_PROFILE_INFO["already_topics_prompt"],
            user_memo,
            strict_mode=STRICT_MODE,
        ),
        system_prompt=PROMPTS[USE_LANGUAGE]["extract"].get_prompt(
            PROMPTS[USE_LANGUAGE]["profile"].get_prompt(project_profiles_slots)
        ),
        temperature=0.2,  # precise
        **PROMPTS[USE_LANGUAGE]["extract"].get_kwargs(),
    )
    if not p.ok():
        return p
    results = p.data()
    # print(
    #     PROMPTS[USE_LANGUAGE]["extract"].pack_input(
    #         CURRENT_PROFILE_INFO["already_topics_prompt"],
    #         user_memo,
    #         strict_mode=STRICT_MODE,
    #     )
    # )
    # print("-------------------------------")
    # print(results)
    parsed_facts: AIUserProfiles = parse_string_into_profiles(results)
    new_facts: list[FactResponse] = parsed_facts.model_dump()["facts"]
    if not len(new_facts):
        TRACE_LOG.info(
            project_id,
            user_id,
            f"No new facts extracted",
        )
        return Promise.resolve(
            {
                "fact_contents": [],
                "fact_attributes": [],
                "profiles": profiles,
                "total_profiles": project_profiles_slots,
            }
        )

    for nf in new_facts:
        nf[ContanstTable.topic] = attribute_unify(nf[ContanstTable.topic])
        nf[ContanstTable.sub_topic] = attribute_unify(nf[ContanstTable.sub_topic])
    new_facts = merge_by_topic_sub_topics(new_facts)

    fact_contents = []
    fact_attributes = []

    for nf in new_facts:
        if CURRENT_PROFILE_INFO["allowed_topic_subtopics"] is not None:
            if (
                nf[ContanstTable.topic],
                nf[ContanstTable.sub_topic],
            ) not in CURRENT_PROFILE_INFO["allowed_topic_subtopics"]:
                continue
        fact_contents.append(nf["memo"])
        fact_attributes.append(
            {
                ContanstTable.topic: nf[ContanstTable.topic],
                ContanstTable.sub_topic: nf[ContanstTable.sub_topic],
            }
        )
    return Promise.resolve(
        {
            "fact_contents": fact_contents,
            "fact_attributes": fact_attributes,
            "profiles": profiles,
            "total_profiles": project_profiles_slots,
        }
    )
