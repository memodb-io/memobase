from ..controllers import full as controllers
from .. import utils

from ..models.response import BaseResponse, CODE
from ..models.utils import Promise
from ..models import response as res
from fastapi import Request
from fastapi import Body


async def update_project_profile_config(
    request: Request,
    profile_config: res.ProfileConfigData = Body(
        ..., description="The profile config to update"
    ),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = utils.is_valid_profile_config(profile_config.profile_config)
    if not p.ok():
        return p.to_response(res.BaseResponse)
    p = await controllers.project.update_project_profile_config(
        project_id, profile_config.profile_config
    )
    return p.to_response(res.BaseResponse)


async def get_project_profile_config_string(
    request: Request,
) -> res.ProfileConfigDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.project.get_project_profile_config_string(project_id)
    return p.to_response(res.ProfileConfigDataResponse)


async def get_project_billing(request: Request) -> res.BillingResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.billing.get_project_billing(project_id)
    return p.to_response(res.BillingResponse)
