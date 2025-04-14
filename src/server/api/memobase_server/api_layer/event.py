from ..controllers import full as controllers
from ..models import response as res
from fastapi import Request
from fastapi import Path, Query, Body


async def get_user_events(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    topk: int = Query(10, description="Number of events to retrieve, default is 10"),
    max_token_size: int = Query(
        None,
        description="Max token size of returned events",
    ),
) -> res.UserEventsDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event.get_user_events(
        user_id, project_id, topk=topk, max_token_size=max_token_size
    )
    return p.to_response(res.UserEventsDataResponse)


async def delete_user_event(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    event_id: str = Path(..., description="The ID of the event"),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event.delete_user_event(user_id, project_id, event_id)
    return p.to_response(res.BaseResponse)


async def update_user_event(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    event_id: str = Path(..., description="The ID of the event"),
    event_data: res.EventData = Body(..., description="Event data to update"),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event.update_user_event(
        user_id, project_id, event_id, event_data.model_dump()
    )
    return p.to_response(res.BaseResponse)


async def search_user_events(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    query: str = Query(..., description="The query to search for"),
    topk: int = Query(10, description="Number of events to retrieve, default is 10"),
    similarity_threshold: float = Query(
        0.5, description="Similarity threshold, default is 0.5"
    ),
    time_range_in_days: int = Query(7, description="Time range in days, default is 7"),
) -> res.UserEventsDataResponse:
    p = await controllers.event.search_user_events(
        user_id, query, topk, similarity_threshold, time_range_in_days
    )
    return p.to_response(res.UserEventsDataResponse)
