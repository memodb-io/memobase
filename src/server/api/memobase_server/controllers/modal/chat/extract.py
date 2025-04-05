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
from ....prompts import validate_profile as validate_profile_prompt
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
    user_id: str, project_id: str, blob_ids: list[str], blobs: list[Blob]
) -> Promise[dict]:
    assert len(blob_ids) == len(blobs), "Length of blob_ids and blobs must be equal"
    assert all(b.type == BlobType.chat for b in blobs), "All blobs must be chat blobs"
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

    blob_strs = tag_chat_blobs_in_order_xml(blobs)
    p = await llm_complete(
        project_id,
        PROMPTS[USE_LANGUAGE]["extract"].pack_input(
            already_topics_prompt,
            blob_strs,
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
    p = await validate_topics(
        project_id, fact_contents, fact_attributes, project_profiles_slots
    )
    if not p.ok():
        return p
    fact_contents = p.data()["fact_contents"]
    fact_attributes = p.data()["fact_attributes"]
    return Promise.resolve(
        {
            "fact_contents": fact_contents,
            "fact_attributes": fact_attributes,
            "profiles": profiles,
            "config": project_profiles,
            "total_profiles": project_profiles_slots,
        }
    )


async def validate_topics(
    project_id: str,
    fact_contents: list[str],
    fact_attributes: list[dict],
    project_profiles: list[UserProfileTopic],
) -> Promise[dict]:
    profile_maps = {
        (up.topic, sp.name): sp for up in project_profiles for sp in up.sub_topics
    }
    # print(profile_maps)
    tasks = []
    update_i = []
    for i, (fc, fa) in enumerate(zip(fact_contents, fact_attributes)):
        topic = fa[ContanstTable.topic]
        sub_topic = fa[ContanstTable.sub_topic]
        if (topic, sub_topic) not in profile_maps:
            continue
        sp_struct = profile_maps[(topic, sub_topic)]
        if not sp_struct.description:
            continue
        if not sp_struct.validate_value:
            continue
        print("Validate", fc, fa)
        tasks.append(
            llm_complete(
                project_id,
                validate_profile_prompt.get_input(
                    topic, sub_topic, fc, sp_struct.description
                ),
                system_prompt=validate_profile_prompt.get_prompt(),
                **validate_profile_prompt.get_kwargs(),
            )
        )
        update_i.append(i)
    results: list[Promise[str]] = await asyncio.gather(*tasks)
    remove_i = set()
    for i, r in zip(update_i, results):
        if not r.ok():
            LOG.error(f"Failed to validate topic {fact_attributes[i]}: {r.msg()}")
            continue
        raw_result = r.data()

        result = parse_string_into_merge_action(raw_result)
        if result is None:
            remove_i.add(i)
            continue
        if result["action"] == "SAVE":
            LOG.info(f"Validate topic {fact_attributes[i]}: {result['memo']}")
            fact_contents[i] = result["memo"]
        else:
            LOG.error(
                f"Invalid action {result['action']} for topic {fact_attributes[i]}"
            )
    LOG.info(f"Remove {len(remove_i)} topics for not valid")
    left_fact_contents = []
    left_fact_attributes = []
    for i in range(len(fact_contents)):
        if i not in remove_i:
            left_fact_contents.append(fact_contents[i])
            left_fact_attributes.append(fact_attributes[i])
    return Promise.resolve(
        {
            "fact_contents": left_fact_contents,
            "fact_attributes": left_fact_attributes,
        }
    )
