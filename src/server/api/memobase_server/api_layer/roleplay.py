import json
from ..controllers import full as controllers
from ..controllers.modal.roleplay import proactive_topics
from ..models.blob import BlobType
from ..models.utils import Promise, CODE
from ..models.response import UUID
from ..models import response as res
from fastapi import Request
from fastapi import Body, Path, Query


async def infer_proactive_topics(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
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
    body: res.ProactiveTopicRequest = Body(..., description="The body of the request"),
) -> res.ProactiveTopicResponse:
    """Provide interest detection and personalized topics"""
    project_id = request.state.memobase_project_id
    topic_limits_json = topic_limits_json or "{}"
    try:
        topic_limits = res.StrIntData(data=json.loads(topic_limits_json)).data
    except Exception as e:
        return Promise.reject(
            CODE.BAD_REQUEST, f"Invalid JSON requests: {e}"
        ).to_response(res.UserProfileResponse)
    p = await proactive_topics.process_messages(
        user_id,
        project_id,
        body.messages,
        body.agent_context,
        prefer_topics,
        topk,
        max_token_size,
        only_topics,
        max_subtopic_size,
        topic_limits,
    )
    return p.to_response(res.ProactiveTopicResponse)
