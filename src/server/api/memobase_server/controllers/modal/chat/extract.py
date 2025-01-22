from ....env import CONFIG, LOG
from ....models.utils import Promise
from ....models.blob import Blob, BlobType
from ....models.response import AIUserProfiles, CODE
from ....llms import llm_complete
from ....prompts.utils import (
    tag_chat_blobs_in_order_xml,
    attribute_unify,
    parse_string_into_profiles,
)
from ...profile import get_user_profiles
from .types import FactResponse, PROMPTS


def merge_by_topic_sub_topics(new_facts: list[FactResponse]):
    topic_subtopic = {}
    for nf in new_facts:
        key = (nf["topic"], nf["sub_topic"])
        if key in topic_subtopic and isinstance(nf["memo"], str):
            topic_subtopic[key]["memo"] += f"; {nf['memo']}"
            continue
        topic_subtopic[key] = nf
    return list(topic_subtopic.values())


async def extract_topics(
    user_id: str, blob_ids: list[str], blobs: list[Blob]
) -> Promise[dict | None]:
    assert len(blob_ids) == len(blobs), "Length of blob_ids and blobs must be equal"
    assert all(b.type == BlobType.chat for b in blobs), "All blobs must be chat blobs"
    p = await get_user_profiles(user_id)
    if not p.ok():
        return p
    profiles = p.data().profiles

    if len(profiles):
        already_topics_subtopics = sorted(
            set([(p.attributes["topic"], p.attributes["sub_topic"]) for p in profiles])
        )
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
        blob_strs,
        system_prompt=PROMPTS[CONFIG.language]["extract"].get_prompt(
            already_topics=already_topics_prompt
        ),
        temperature=0.2,  # precise
    )
    if not p.ok():
        return p
    results = p.data()
    parsed_facts: AIUserProfiles = parse_string_into_profiles(results)
    new_facts: list[FactResponse] = parsed_facts.model_dump()["facts"]
    if not len(new_facts):
        LOG.info(f"No new facts extracted {user_id}")
        return Promise.resolve(None)

    for nf in new_facts:
        nf["topic"] = attribute_unify(nf["topic"])
        nf["sub_topic"] = attribute_unify(nf["sub_topic"])
    new_facts = merge_by_topic_sub_topics(new_facts)

    fact_contents = []
    fact_attributes = []

    for nf in new_facts:
        fact_contents.append(nf["memo"])
        fact_attributes.append(
            {
                "topic": nf["topic"],
                "sub_topic": nf["sub_topic"],
            }
        )
    return Promise.resolve(
        {
            "fact_contents": fact_contents,
            "fact_attributes": fact_attributes,
            "profiles": profiles,
        }
    )
