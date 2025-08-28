import json
from fastapi import Request
from fastapi import Path, Query, Body
from datetime import datetime
from ..controllers import full as controllers
from ..controllers.post_process.profile import filter_profiles_with_chats

from ..models.response import CODE, UUID
from ..models.utils import Promise
from ..models.blob import BlobType
from ..models import response as res


async def get_user_profile(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user to get profiles for"),
    topk: int = Query(
        None, description="Number of profiles to retrieve, default is all"
    ),
    max_token_size: int = Query(
        None,
        description="Max token size of returned profile content, default is all",
    ),
    prefer_topics: list[str] = Query(
        None,
        description="Rank prefer topics at first to try to keep them in filtering, default order is by updated time",
    ),
    only_topics: list[str] = Query(
        None,
        description="Only return profiles with these topics, default is all",
    ),
    max_subtopic_size: int = Query(
        None,
        description="Max subtopic size of the same topic in returned profile, default is all",
    ),
    topic_limits_json: str = Query(
        None,
        description='Set specific subtopic limits for topics in JSON, for example {"topic1": 3, "topic2": 5}. The limits in this param will override `max_subtopic_size`.',
    ),
    chats_str: str = Query(
        None,
        description='List of chats in OpenAI Message format, for example: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]',
    ),
) -> res.UserProfileResponse:
    """Get the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    topic_limits_json = topic_limits_json or "{}"
    chats_str = chats_str or "[]"
    try:
        topic_limits = res.StrIntData(data=json.loads(topic_limits_json)).data
        chats = res.MessageData(data=json.loads(chats_str)).data
    except Exception as e:
        return Promise.reject(
            CODE.BAD_REQUEST, f"Invalid JSON requests: {e}"
        ).to_response(res.UserProfileResponse)
    p = await controllers.profile.get_user_profiles(user_id, project_id)
    if not p.ok():
        return p.to_response(res.UserProfileResponse)
    total_profiles = p.data()
    if chats:
        p = await filter_profiles_with_chats(
            user_id,
            project_id,
            total_profiles,
            chats,
            only_topics=only_topics,
            # max_filter_num=topk,
        )
        if p.ok():
            total_profiles.profiles = p.data()["profiles"]
    p = await controllers.profile.truncate_profiles(
        total_profiles,
        prefer_topics=prefer_topics,
        topk=topk,
        max_token_size=max_token_size,
        only_topics=only_topics,
        max_subtopic_size=max_subtopic_size,
        topic_limits=topic_limits,
    )
    return p.to_response(res.UserProfileResponse)


async def delete_user_profile(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    profile_id: UUID = Path(..., description="The ID of the profile to delete"),
) -> res.BaseResponse:
    """Delete a profile"""
    project_id = request.state.memobase_project_id
    p = await controllers.profile.delete_user_profile(user_id, project_id, profile_id)
    return p.to_response(res.IdResponse)


async def update_user_profile(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    profile_id: UUID = Path(..., description="The ID of the profile to update"),
    content: res.ProfileDelta = Body(
        ..., description="The content of the profile to update"
    ),
) -> res.BaseResponse:
    """Update the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    p = await controllers.profile.update_user_profiles(
        user_id, project_id, [profile_id], [content.content], [content.attributes]
    )
    if p.ok():
        return Promise.resolve(None).to_response(res.BaseResponse)
    return Promise.reject(p.code(), p.msg()).to_response(res.BaseResponse)


async def add_user_profile(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    content: res.ProfileDelta = Body(
        ..., description="The content of the profile to add"
    ),
) -> res.IdResponse:
    """Add the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    p = await controllers.profile.add_user_profiles(
        user_id, project_id, [content.content], [content.attributes]
    )
    if p.ok():
        return Promise.resolve(res.IdData(id=p.data().ids[0])).to_response(
            res.IdResponse
        )
    return Promise.reject(p.code(), p.msg()).to_response(res.IdResponse)


async def import_user_context(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    content: res.UserContextImport = Body(
        ..., description="The content of the user context to import"
    ),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.billing.get_project_billing(project_id)
    if not p.ok():
        return p.to_response(res.IdResponse)
    billing = p.data()

    if billing.token_left is not None and billing.token_left < 0:
        return Promise.reject(
            CODE.SERVICE_UNAVAILABLE,
            f"Your project reaches Memobase token limit, "
            f"Left: {billing.token_left}, this project used: {billing.project_token_cost_month}. "
            f"Your quota will be refilled on {billing.next_refill_at}. "
            "\nhttps://www.memobase.io/pricing for more information.",
        ).to_response(res.BaseResponse)

    prompt = f"""Below is my information, please remember them:
{content.context}
"""
    blob_data = res.BlobData(
        blob_type=BlobType.chat,
        blob_data={
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        },
    )
    p = await controllers.buffer.flush_buffer(user_id, project_id, BlobType.chat)
    if not p.ok():
        return p.to_response(res.BaseResponse)

    p = await controllers.blob.insert_blob(user_id, project_id, blob_data)
    if not p.ok():
        return p.to_response(res.BaseResponse)

    # TODO if single user insert too fast will cause random order insert to buffer
    # So no background task for insert buffer yet
    pb = await controllers.buffer.insert_blob_to_buffer(
        user_id, project_id, p.data().id, blob_data.to_blob()
    )
    if not pb.ok():
        return pb.to_response(res.BaseResponse)

    p = await controllers.buffer.flush_buffer(user_id, project_id, BlobType.chat)
    if not p.ok():
        return p.to_response(res.BaseResponse)
    return Promise.resolve(None).to_response(res.BaseResponse)
