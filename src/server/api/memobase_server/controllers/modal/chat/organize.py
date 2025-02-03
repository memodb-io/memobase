import asyncio
from collections import defaultdict
from .types import MergeAddResult, PROMPTS, AddProfile
from ....prompts.types import get_specific_subtopics, attribute_unify
from ....prompts.utils import parse_string_into_subtopics
from ....models.utils import Promise
from ....models.response import ProfileData
from ....env import CONFIG, LOG
from ....llms import llm_complete


async def organize_profiles(profile_options: MergeAddResult) -> Promise[None]:
    profiles = profile_options["before_profiles"]
    topic_groups = defaultdict(list)
    for p in profiles:
        topic_groups[p.attributes["topic"]].append(p)

    need_to_organize_topics: dict[str, list[ProfileData]] = {}
    for topic, group in topic_groups.items():
        if len(group) > CONFIG.max_profile_subtopics:
            need_to_organize_topics[topic] = group

    if not len(need_to_organize_topics):
        return Promise.resolve(None)
    ps = await asyncio.gather(
        *[
            organize_profiles_by_topic(group)
            for group in need_to_organize_topics.values()
        ]
    )
    if not all([p.ok() for p in ps]):
        errmsg = "\n".join([p.msg() for p in ps if not p.ok()])
        return Promise.reject(f"Failed to organize profiles: {errmsg}")

    delete_profile_ids = []
    for gs in need_to_organize_topics.values():
        delete_profile_ids.extend([p.id for p in gs])
    new_profiles = []
    for p in ps:
        new_profiles.extend(p.data())

    profile_options["add"].extend(new_profiles)
    profile_options["add"] = deduplicate_profiles(profile_options["add"])
    profile_options["delete"].extend(delete_profile_ids)
    return Promise.resolve(None)


async def organize_profiles_by_topic(
    profiles: list[ProfileData],  # profiles in the same topics
) -> Promise[list[AddProfile]]:
    assert (
        len(profiles) > CONFIG.max_profile_subtopics
    ), f"Unknown Error,{len(profiles)} is not greater than max_profile_subtopics: {CONFIG.max_profile_subtopics}"
    assert all(
        p.attributes["topic"] == profiles[0].attributes["topic"] for p in profiles
    ), f"Unknown Error, all profiles are not in the same topic: {profiles[0].attributes['topic']}"
    LOG.info(
        f"Organizing profiles for topic: {profiles[0].attributes['topic']} with sub_topics {len(profiles)}"
    )
    topic = attribute_unify(profiles[0].attributes["topic"])
    suggest_subtopics = get_specific_subtopics(
        topic, PROMPTS[CONFIG.language]["profile"]
    )

    llm_inputs = "\n".join(
        [
            f"- {p.attributes['sub_topic']}{CONFIG.llm_tab_separator}{p.content}"
            for p in profiles
        ]
    )
    llm_prompt = f"""topic: {topic}
{llm_inputs}
"""
    p = await llm_complete(
        llm_prompt,
        PROMPTS[CONFIG.language]["organize"].get_prompt(
            CONFIG.max_profile_subtopics // 2 + 1, suggest_subtopics
        ),
        temperature=0.2,  # precise
        **PROMPTS[CONFIG.language]["organize"].get_kwargs(),
    )
    if not p.ok():
        return p
    results = p.data()
    subtopics = parse_string_into_subtopics(results)
    reorganized_profiles: list[AddProfile] = [
        {
            "content": sp["memo"],
            "attributes": {
                "topic": topic,
                "sub_topic": sp["sub_topic"],
            },
        }
        for sp in subtopics
    ]
    if len(reorganized_profiles) == 0:
        return Promise.reject(
            "Failed to organize profiles, left profiles is 0 so maybe it's the LLM error"
        )
    return Promise.resolve(reorganized_profiles)


def deduplicate_profiles(profiles: list[AddProfile]) -> list[AddProfile]:
    topic_subtopic = {}
    for nf in profiles:
        key = (nf["attributes"]["topic"], nf["attributes"]["sub_topic"])
        if key in topic_subtopic:
            topic_subtopic[key]["content"] += f"; {nf['content']}"
            continue
        topic_subtopic[key] = nf
    return list(topic_subtopic.values())
