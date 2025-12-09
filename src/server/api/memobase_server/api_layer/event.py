from ..controllers import full as controllers
from ..models import response as res
from ..models.response import UUID
from fastapi import Request
from fastapi import Path, Query, Body


async def get_user_events(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    topk: int = Query(10, description="Number of events to retrieve, default is 10"),
    max_token_size: int = Query(
        None,
        description="Max token size of returned events",
    ),
    need_summary: bool = Query(
        False,
        description="Whether to return events with summaries",
    ),
) -> res.UserEventsDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event.get_user_events(
        user_id, project_id, topk=topk, need_summary=need_summary
    )
    if not p.ok():
        return p.to_response(res.UserEventsDataResponse)
    p = await controllers.event.truncate_events(p.data(), max_token_size)
    return p.to_response(res.UserEventsDataResponse)


async def delete_user_event(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    event_id: UUID = Path(..., description="The ID of the event"),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event.delete_user_event(user_id, project_id, event_id)
    return p.to_response(res.BaseResponse)


async def update_user_event(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    event_id: UUID = Path(..., description="The ID of the event"),
    event_data: res.EventData = Body(..., description="Event data to update"),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event.update_user_event(
        user_id, project_id, event_id, event_data.model_dump()
    )
    return p.to_response(res.BaseResponse)


async def search_user_events(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    query: str = Query(..., description="The query to search for"),
    topk: int = Query(10, description="Number of events to retrieve, default is 10"),
    similarity_threshold: float = Query(
        0.2, description="Similarity threshold, default is 0.2"
    ),
    time_range_in_days: int = Query(
        180, description="Only allow events within the past few days, default is 180"
    ),
) -> res.UserEventsDataResponse:
    project_id = request.state.memobase_project_id

    p = await controllers.event.search_user_events(
        user_id, project_id, query, topk, similarity_threshold, time_range_in_days
    )
    return p.to_response(res.UserEventsDataResponse)


async def search_user_event_gists(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    query: str = Query(..., description="The query to search for"),
    topk: int = Query(10, description="Number of events to retrieve, default is 10"),
    similarity_threshold: float = Query(
        0.2, description="Similarity threshold, default is 0.2"
    ),
    time_range_in_days: int = Query(
        180, description="Only allow events within the past few days, default is 180"
    ),
) -> res.UserEventGistsDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event_gist.search_user_event_gists(
        user_id, project_id, query, topk, similarity_threshold, time_range_in_days
    )
    return p.to_response(res.UserEventGistsDataResponse)


async def search_user_events_by_tags(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    tags: str = Query(
        None,
        description="Comma-separated list of tag names that events must have (e.g.'emotion,romance')",
    ),
    tag_values: str = Query(
        None,
        description="Comma-separated tag=value pairs for exact matches (e.g., 'emotion=happy,topic=work')",
    ),
    topk: int = Query(10, description="Number of events to retrieve, default is 10"),
) -> res.UserEventsDataResponse:
    project_id = request.state.memobase_project_id

    has_event_tag = None
    if tags:
        has_event_tag = [tag.strip() for tag in tags.split(",") if tag.strip()]

    event_tag_equal = None
    if tag_values:
        event_tag_equal = {}
        for pair in tag_values.split(","):
            if "=" in pair:
                tag_name, tag_value = pair.split("=", 1)
                event_tag_equal[tag_name.strip()] = tag_value.strip()

    p = await controllers.event.filter_user_events(
        user_id, project_id, has_event_tag, event_tag_equal, topk
    )

    return p.to_response(res.UserEventsDataResponse)
