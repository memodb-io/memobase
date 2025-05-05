import asyncio
from ....env import CONFIG, LOG, ContanstTable
from ....models.utils import Promise
from ....models.blob import Blob, BlobType
from ....models.response import AIUserProfiles, CODE
from ....llms import llm_complete
from ....prompts.utils import (
    tag_chat_blobs_in_order_xml,
    attribute_unify,
    parse_string_into_profiles,
    parse_string_into_merge_action,
)
from ....prompts.profile_init_utils import read_out_profile_config, UserProfileTopic
from ...profile import get_user_profiles
from ...project import get_project_profile_config

# from ...project impor
from .types import FactResponse, PROMPTS


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
    user_id: str, project_id: str, user_memo: str
) -> Promise[dict]:
    p = await get_user_profiles(user_id, project_id)
    if not p.ok():
        return p
    profiles = p.data().profiles
    p = await get_project_profile_config(project_id)
    if not p.ok():
        return p
    project_profiles = p.data()
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
        if STRICT_MODE:
            already_topics_subtopics = already_topics_subtopics.intersection(
                allowed_topic_subtopics
            )
        already_topics_subtopics = sorted(already_topics_subtopics)
        already_topics_prompt = "\n".join(
            [
                f"- {topic}{CONFIG.llm_tab_separator}{sub_topic}"
                for topic, sub_topic in already_topics_subtopics
            ]
        )
        LOG.info(
            f"User {user_id} already have {len(profiles)} profiles, {len(already_topics_subtopics)} topics"
        )
    else:
        already_topics_prompt = ""

    p = await llm_complete(
        project_id,
        PROMPTS[USE_LANGUAGE]["extract"].pack_input(
            already_topics_prompt,
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
    # print(user_memo)
    # print("-------------------------------")
    # print(results)
    parsed_facts: AIUserProfiles = parse_string_into_profiles(results)
    new_facts: list[FactResponse] = parsed_facts.model_dump()["facts"]
    if not len(new_facts):
        LOG.info(f"No new facts extracted {user_id}")
        return Promise.resolve(
            {
                "fact_contents": [],
                "fact_attributes": [],
                "profiles": profiles,
                "config": project_profiles,
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
        if STRICT_MODE:
            if (
                nf[ContanstTable.topic],
                nf[ContanstTable.sub_topic],
            ) not in allowed_topic_subtopics:
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
            "config": project_profiles,
            "total_profiles": project_profiles_slots,
        }
    )
