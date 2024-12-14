import asyncio
from typing import TypedDict
import pydantic
from ...env import CONFIG, LOG
from ...utils import get_blob_str, get_encoded_tokens
from ...models.utils import Promise
from ...models.blob import Blob, BlobType
from ...models.response import ProfileData, AIUserProfiles, CODE
from ...llms import llm_complete
from ...prompts import (
    extract_profile,
    merge_profile,
    summary_profile,
    zh_extract_profile,
    zh_merge_profile,
)
from ...prompts.utils import (
    tag_blobs_in_order_xml,
    attribute_unify,
    parse_string_into_profiles,
    parse_string_into_merge_action,
)
from ..profile import get_user_profiles, update_user_profile, add_user_profiles

FactResponse = TypedDict(
    "Facts", {"topic": str, "sub_topic": str, "memo": str, "cites": list[int]}
)
UpdateResponse = TypedDict("Facts", {"action": str, "memo": str})


PROMPTS = {
    "en": {"extract": extract_profile, "merge": merge_profile},
    "zh": {"extract": zh_extract_profile, "merge": zh_merge_profile},
}


def merge_by_topic_sub_topics(new_facts: list[FactResponse]):
    topic_subtopic = {}
    for nf in new_facts:
        key = (nf["topic"], nf["sub_topic"])
        if key in topic_subtopic:
            if isinstance(nf["memo"], str):
                topic_subtopic[key]["memo"] += f"; {nf['memo']}"
                topic_subtopic[key]["cites"] += nf["cites"]
                continue
        topic_subtopic[key] = nf
    return list(topic_subtopic.values())


async def process_blobs(
    user_id: str, blob_ids: list[str], blobs: list[Blob]
) -> Promise[None]:
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

    blob_strs = tag_blobs_in_order_xml(blobs, tag_name="chat")
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

    related_blob_ids = []
    fact_contents = []
    fact_attributes = []

    # FIXME if two same attributes in fact_attributes, will cause duplicate in profiles to add
    for nf in new_facts:
        fact_contents.append(nf["memo"])
        fact_attributes.append(
            {
                "topic": nf["topic"],
                "sub_topic": nf["sub_topic"],
            }
        )
        related_blob_ids.append([blob_ids[i] for i in nf["cites"] if i < len(blob_ids)])
    p = await merge_or_add_new_memos(
        user_id, fact_contents, fact_attributes, related_blob_ids, profiles
    )
    if not p.ok():
        return p
    return Promise.resolve(None)


async def merge_or_add_new_memos(
    user_id: str,
    fact_contents: list[str],
    fact_attributes: list[dict],
    related_blob_ids: list[list[str]],
    profiles: list[ProfileData],
) -> Promise[None]:
    if not len(profiles):
        p = await add_user_profiles(
            user_id, fact_contents, fact_attributes, related_blob_ids
        )
        if not p.ok():
            return p
        return Promise.resolve(None)

    new_facts_to_add = []
    facts_to_update = []
    for f_c, f_a, r_b in zip(fact_contents, fact_attributes, related_blob_ids):
        new_p = {"content": f_c, "attributes": f_a, "related_blobs": r_b}
        same_topic_p = [
            p
            for p in profiles
            if (
                p.attributes["topic"] == f_a["topic"]
                and p.attributes["sub_topic"] == f_a["sub_topic"]
            )
        ]
        # 1 if not same topics exist, directly add this
        if not len(same_topic_p):
            new_facts_to_add.append(new_p)
            continue
        same_topic_p = same_topic_p[0]
        # 2 if exist, continue to merge/replace
        facts_to_update.append(
            {
                "old_profile": same_topic_p,
                "new_profile": new_p,
            }
        )
    p = await add_user_profiles(
        user_id,
        [p["content"] for p in new_facts_to_add],
        [p["attributes"] for p in new_facts_to_add],
        [p["related_blobs"] for p in new_facts_to_add],
    )
    if not p.ok():
        return p
    merge_tasks = []
    for dp in facts_to_update:
        old_p: ProfileData = dp["old_profile"]
        task = llm_complete(
            PROMPTS[CONFIG.language]["merge"].get_input(
                old_p.attributes["topic"],
                old_p.attributes["sub_topic"],
                old_p.content,
                dp["new_profile"]["content"],
            ),
            system_prompt=PROMPTS[CONFIG.language]["merge"].get_prompt(),
            temperature=0.2,  # precise
        )
        merge_tasks.append(task)

    success_update_profile_count = 0
    update_merge_profile_count = 0
    update_replace_profile_count = 0
    merge_results: list[Promise] = await asyncio.gather(*merge_tasks)
    for p, old_new_profile in zip(merge_results, facts_to_update):
        if not p.ok():
            LOG.warning(f"Failed to merge profiles: {p.msg()}")
            continue
        old_p: ProfileData = old_new_profile["old_profile"]

        update_response: UpdateResponse = parse_string_into_merge_action(p.data())
        print(update_response)
        if update_response is None:
            LOG.warning(f"Failed to parse merge action: {p.data()}")
            continue
        if (
            len(get_encoded_tokens(update_response["memo"]))
            > CONFIG.max_pre_profile_token_size
        ):
            LOG.warning(
                f"Profile too long: {update_response['memo'][:100]}, summarizing"
            )
            sum_memo = await summary_memo(update_response["memo"])
            if not sum_memo.ok():
                LOG.warning(
                    f"Failed to summarize: {update_response['memo'][:100]}, abort update"
                )
                continue
            update_response["memo"] = sum_memo.data()
        if update_response["action"] == "REPLACE":
            p = await update_user_profile(
                user_id,
                old_p.id,
                old_p.attributes,
                update_response["memo"],
                old_new_profile["new_profile"]["related_blobs"],
            )
            update_replace_profile_count += 1
        elif update_response["action"] == "MERGE":
            p = await update_user_profile(
                user_id,
                old_p.id,
                old_p.attributes,
                update_response["memo"],
                old_p.related_blobs + old_new_profile["new_profile"]["related_blobs"],
            )
            update_merge_profile_count += 1
        else:
            LOG.warning(f"Invalid action: {update_response['action']}")
            continue
        if not p.ok():
            LOG.warning(f"Failed to update profiles: {p.msg()}")
            continue
        success_update_profile_count += 1
    LOG.info(
        (
            f"TOTAL {len(fact_contents)} profiles, ADD {len(new_facts_to_add)} new profiles, "
            f"update {success_update_profile_count}/{len(facts_to_update)} existing profiles, "
            f"REPLACE:MERGE = {update_replace_profile_count}:{update_merge_profile_count}"
        )
    )
    return Promise.resolve(None)


async def summary_memo(profile: str) -> Promise[str]:
    result = await llm_complete(
        profile,
        system_prompt=summary_profile.get_prompt(),
        temperature=0.2,  # precise
    )
    return result
