from ..controllers import full as controllers
from .. import utils

from ..models.response import BaseResponse, CODE
from ..models.utils import Promise
from ..models import response as res
from fastapi import Request, Response
from typing import Literal
from fastapi import Body, Path, Query


async def update_project_profile_config(
    request: Request,
    response: Response,
    profile_config: res.ProfileConfigData = Body(
        ..., description="The profile config to update"
    ),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = utils.is_valid_profile_config(profile_config.profile_config)
    if not p.ok():
        response.status_code = p.code()
        return p.to_response(res.BaseResponse)
    p = await controllers.project.update_project_profile_config(
        project_id, profile_config.profile_config
    )
    if p.ok():
        response.status_code = 200
    else:
        response.status_code = p.code()
    return p.to_response(res.BaseResponse)


async def get_project_profile_config_string(
    request: Request,
    response: Response,
) -> res.ProfileConfigDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.project.get_project_profile_config_string(project_id)
    if p.ok():
        response.status_code = 200
    else:
        response.status_code = p.code()
    return p.to_response(res.ProfileConfigDataResponse)


async def get_project_billing(request: Request) -> res.BillingResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.billing.get_project_billing(project_id)
    return p.to_response(res.BillingResponse)


async def get_project_users(
    request: Request,
    response: Response,
    search: str = Query("", description="Search string in username field"),
    order_by: Literal["updated_at", "profile_count", "event_count"] = Query(
        "updated_at", description="Order by field"
    ),
    order_desc: bool = Query(True, description="Order descending or ascending"),
    limit: int = Query(10, description="Limit the number of results returned"),
    offset: int = Query(0, description="Offset the starting point for pagination"),
) -> res.ProjectUsersDataResponse:
    """
    Get the users of a project in different orders
    """
    project_id = request.state.memobase_project_id
    users = await controllers.project.get_project_users(
        project_id, search, limit, offset, order_by, order_desc
    )
    if users.ok():
        response.status_code = 200
    else:
        response.status_code = users.code()
    return users.to_response(res.ProjectUsersDataResponse)


async def get_project_usage(
    request: Request,
    response: Response,
    last_days: int = Query(7, description="The number of days to get"),
) -> res.UsageResponse:
    """
    Get the usage of a project in the last days
    """
    project_id = request.state.memobase_project_id
    p = await controllers.project.get_project_usage(project_id, last_days)
    if p.ok():
        response.status_code = 200
    else:
        response.status_code = p.code()
    return p.to_response(res.UsageResponse)
