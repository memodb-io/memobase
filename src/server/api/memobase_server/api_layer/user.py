from ..controllers import full as controllers

from ..models.response import BaseResponse, UUID
from ..models.blob import BlobType
from ..models import response as res
from fastapi import Request
from fastapi import Path, Query, Body


async def create_user(
    request: Request,
    user_data: res.UserData = Body(
        ..., description="User data for creating a new user"
    ),
) -> res.IdResponse:
    """Create a new user with additional data"""
    project_id = request.state.memobase_project_id
    p = await controllers.user.create_user(user_data, project_id)
    return p.to_response(res.IdResponse)


async def get_user(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user to retrieve"),
) -> res.UserDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.get_user(user_id, project_id)
    return p.to_response(res.UserDataResponse)


async def update_user(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user to update"),
    user_data: dict = Body(..., description="Updated user data"),
) -> res.IdResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.update_user(user_id, project_id, user_data)
    return p.to_response(res.IdResponse)


async def delete_user(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user to delete"),
) -> BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.delete_user(user_id, project_id)
    return p.to_response(BaseResponse)


async def get_user_all_blobs(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user to fetch blobs for"),
    blob_type: BlobType = Path(..., description="The type of blobs to retrieve"),
    page: int = Query(0, description="Page number for pagination, starting from 0"),
    page_size: int = Query(10, description="Number of items per page, default is 10"),
) -> res.IdsResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.get_user_all_blobs(
        user_id, project_id, blob_type, page, page_size
    )
    return p.to_response(res.IdsResponse)
