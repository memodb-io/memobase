import asyncio

from ....models.blob import Blob
from ....models.utils import Promise
from ...profile import add_user_profiles, update_user_profiles
from .extract import extract_topics
from .merge import merge_or_add_new_memos
from .summary import re_summary


async def process_blobs(
    user_id: str, blob_ids: list[str], blobs: list[Blob]
) -> Promise[None]:
    p = await extract_topics(user_id, blob_ids, blobs)
    if not p.ok() or p.data() is None:
        return p
    extracted_data = p.data()
    p = await merge_or_add_new_memos(
        fact_contents=extracted_data["fact_contents"],
        fact_attributes=extracted_data["fact_attributes"],
        profiles=extracted_data["profiles"],
    )
    if not p.ok() or p.data() is None:
        return p
    profile_options = p.data()
    await re_summary(
        add_profile=profile_options["add"],
        update_profile=profile_options["update"],
    )

    task_add = add_user_profiles(
        user_id,
        [ap["content"] for ap in profile_options["add"]],
        [ap["attributes"] for ap in profile_options["add"]],
    )
    task_update = update_user_profiles(
        user_id,
        [up["profile_id"] for up in profile_options["update"]],
        [up["content"] for up in profile_options["update"]],
        [up["attributes"] for up in profile_options["update"]],
    )
    ps = await asyncio.gather(task_add, task_update)
    if not all([p.ok() for p in ps]):
        return Promise.reject("Failed to add or update profiles")
    return Promise.resolve(None)
