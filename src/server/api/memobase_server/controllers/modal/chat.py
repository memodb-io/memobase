import asyncio
from typing import TypedDict
from ...env import LOG, pprint
from ...utils import get_blob_str
from ...models.utils import Promise
from ...models.blob import Blob, BlobType
from ...models.response import ProfileData
from ...llms import llm_complete
from ...prompts import extract_profile, merge_profile
from ...prompts.utils import tag_strings_in_order_xml, attribute_unify
from ..user import add_user_profiles, get_user_profiles, update_user_profile

FactResponse = TypedDict(
    "Facts", {"topic": str, "sub_topic": str, "memo": str, "cites": list[int]}
)
UpdateResponse = TypedDict("Facts", {"action": str, "memo": str})


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
        already_topics_prompt = "- " + "\n- ".join(
            [
                f"topic: {topic}, sub_topic: {sub_topic}"
                for topic, sub_topic in already_topics_subtopics
            ]
        )
        LOG.info(
            f"User {user_id} already have {len(profiles)} profiles, {len(already_topics_subtopics)} topics"
        )
    else:
        already_topics_prompt = ""

    blob_strs = tag_strings_in_order_xml(
        [get_blob_str(b) for b in blobs], tag_name="chat"
    )
    p = await llm_complete(
        blob_strs,
        system_prompt=extract_profile.get_prompt(already_topics=already_topics_prompt),
        json_mode=True,
        temperature=0.2,  # precise
    )
    if not p.ok():
        return p
    results = p.data()
    new_facts: list[FactResponse] = results["facts"]

    related_blob_ids = []
    fact_contents = []
    fact_attributes = []
    for nf in new_facts:
        fact_contents.append(nf["memo"])
        fact_attributes.append(
            {
                "topic": attribute_unify(nf["topic"]),
                "sub_topic": attribute_unify(nf["sub_topic"]),
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
            merge_profile.get_input(
                old_p.attributes["topic"],
                old_p.attributes["sub_topic"],
                old_p.content,
                dp["new_profile"]["content"],
            ),
            system_prompt=merge_profile.get_prompt(),
            json_mode=True,
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
        update_response: UpdateResponse = p.data()
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
