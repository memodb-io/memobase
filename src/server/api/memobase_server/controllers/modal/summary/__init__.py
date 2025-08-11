import asyncio

from sqlalchemy.sql.functions import user
from ...project import get_project_profile_config
from ...profile import get_user_profiles
from ....models.blob import Blob, SummaryBlob
from ....utils import get_blob_str, get_encoded_tokens
from ....models.blob import Blob
from ....models.utils import Promise, CODE
from ....models.response import IdsData, ChatModalResponse
from ..chat import (
    process_profile_res,
    process_event_res,
    handle_session_event,
    handle_user_profile_db,
)


def pack_summary(blobs: list[Blob]) -> str:
    return "\n".join([get_blob_str(b) for b in blobs])


async def process_blobs(user_id: str, project_id: str, blobs: list[Blob]):
    if len(blobs) == 0:
        return Promise.reject(
            CODE.SERVER_PARSE_ERROR, "No blobs to process after truncating"
        )

    p = await get_project_profile_config(project_id)
    if not p.ok():
        return p
    project_profiles = p.data()

    p = await get_user_profiles(user_id, project_id)
    if not p.ok():
        return p
    current_user_profiles = p.data()

    user_memo_str = pack_summary(blobs)

    processing_results = await asyncio.gather(
        process_profile_res(
            user_id, project_id, user_memo_str, project_profiles, current_user_profiles
        ),
        process_event_res(
            user_id, project_id, user_memo_str, project_profiles, current_user_profiles
        ),
    )

    profile_results: Promise = processing_results[0]
    event_results: Promise = processing_results[1]

    if not profile_results.ok() or not event_results.ok():
        return Promise.reject(
            CODE.SERVER_PARSE_ERROR,
            f"Failed to process profile or event: {profile_results.msg()}, {event_results.msg()}",
        )

    intermediate_profile, delta_profile_data = profile_results.data()
    event_tags = event_results.data()

    p = await handle_session_event(
        user_id,
        project_id,
        user_memo_str,
        delta_profile_data,
        event_tags,
        project_profiles,
    )
    if not p.ok():
        return p
    eid = p.data()

    p = await handle_user_profile_db(user_id, project_id, intermediate_profile)
    if not p.ok():
        return p
    return Promise.resolve(
        ChatModalResponse(
            event_id=eid,
            add_profiles=p.data().ids,
            update_profiles=[up["profile_id"] for up in intermediate_profile["update"]],
            delete_profiles=intermediate_profile["delete"],
        )
    )
