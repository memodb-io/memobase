from typing import TypedDict
from ...env import LOG, pprint
from ...utils import get_blob_str
from ...models.utils import Promise
from ...models.blob import Blob, BlobType
from ...llms import llm_complete
from ...prompts import extract_fact
from ...prompts import merge_fact
from ...prompts.utils import tag_strings_in_order_xml
from ..user import add_user_profiles, get_user_profiles, update_user_profile

FactResponse = TypedDict("Facts", {"memo": str, "cites": list[int]})
UpdateResponse = TypedDict("Facts", {"old_index": int, "new_index": int, "memo": str})


async def process_blobs(
    user_id: str, blob_ids: list[str], blobs: list[Blob]
) -> Promise[None]:
    assert len(blob_ids) == len(blobs), "Length of blob_ids and blobs must be equal"
    assert all(b.type == BlobType.chat for b in blobs), "All blobs must be chat blobs"

    blob_strs = tag_strings_in_order_xml(
        [get_blob_str(b) for b in blobs], tag_name="chat"
    )
    p = await llm_complete(
        blob_strs, system_prompt=extract_fact.get_prompt(), json_mode=True
    )
    if not p.ok():
        return p
    results = p.data()
    new_facts: list[FactResponse] = results["facts"]

    related_blob_ids = []
    fact_contents = []
    for nf in new_facts:
        related_blob_ids.append([blob_ids[i] for i in nf["cites"] if i < len(blob_ids)])
        fact_contents.append(nf["memo"])

    p = await get_user_profiles(user_id)
    if not p.ok():
        return p
    profiles = p.data().profiles

    if not len(profiles):
        p = await add_user_profiles(user_id, fact_contents, related_blob_ids)
        if not p.ok():
            return p
    else:
        old_new_memos = "\n".join(
            [
                tag_strings_in_order_xml(
                    [p.content for p in profiles], tag_name="old_memo"
                ),
                tag_strings_in_order_xml(fact_contents, tag_name="new_memo"),
            ]
        )
        print("!!!", old_new_memos)
        p = await llm_complete(
            old_new_memos, system_prompt=merge_fact.get_prompt(), json_mode=True
        )
        if not p.ok():
            return p

        add_update_op = p.data()
        add_index = [
            p["new_index"]
            for p in add_update_op["ADD"]
            if p["new_index"] < len(fact_contents)
        ]
        p = await add_user_profiles(
            user_id,
            [fact_contents[i] for i in add_index],
            [related_blob_ids[i] for i in add_index],
        )
        if not p.ok():
            return p

        update_op: list[UpdateResponse] = add_update_op["UPDATE"]

        for dp in update_op:
            # ignore illegal index
            if dp["old_index"] >= len(profiles) or dp["new_index"] >= len(
                fact_contents
            ):
                continue
            p = await update_user_profile(
                user_id,
                profiles[dp["old_index"]].id,
                dp["memo"],
                profiles[dp["old_index"]].related_blobs
                + related_blob_ids[dp["new_index"]],
            )

            if not p.ok():
                return p
        LOG.info(
            f"ADD {len(add_index)} new memo, UPDATE {len(update_op)} old memo for user {user_id}"
        )
    return Promise.resolve(None)
