import time
import memobase_server.env

# Done setting up env

import os
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Request
from fastapi import Path, Query, Body
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from memobase_server.connectors import (
    db_health_check,
    redis_health_check,
    close_connection,
    init_redis_pool,
)
from memobase_server import utils
from memobase_server.models.database import DEFAULT_PROJECT_ID
from memobase_server.models.response import BaseResponse, CODE
from memobase_server.models.blob import BlobType
from memobase_server.models.utils import Promise
from memobase_server.models import response as res
from memobase_server import controllers
from memobase_server.telemetry import telemetry_manager, CounterMetricName, HistogramMetricName
from memobase_server.env import (
    LOG,
    TelemetryKeyName,
    ProjectStatus,
    USAGE_TOKEN_LIMIT_MAP,
)
from memobase_server.telemetry.capture_key import capture_int_key, get_int_key
from uvicorn.config import LOGGING_CONFIG
from memobase_server.auth.token import (
    parse_project_id,
    check_project_secret,
    get_project_status,
)
from memobase_server import utils

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_redis_pool()
    LOG.info(f"Start Memobase Server {memobase_server.__version__} 🖼️")
    yield
    await close_connection()


app = FastAPI(
    summary="APIs for Memobase, a user memory system for LLM Apps",
    version=memobase_server.__version__,
    title="Memobase API",
    lifespan=lifespan,
)
router = APIRouter(prefix="/api/v1")
LOGGING_CONFIG["formatters"]["default"][
    "fmt"
] = "%(levelprefix)s %(asctime)s %(message)s"
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

LOGGING_CONFIG["formatters"]["default"][
    "fmt"
] = "%(levelprefix)s %(asctime)s %(message)s"
LOGGING_CONFIG["formatters"]["access"][
    "fmt"
] = "%(levelprefix)s %(asctime)s %(client_addr)s - %(request_line)s %(status_code)s"
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"


@router.get("/healthcheck", tags=["chore"])
async def healthcheck() -> BaseResponse:
    """Check if your memobase is set up correctly"""
    LOG.info("Healthcheck requested")
    if not db_health_check():
        raise HTTPException(
            status_code=CODE.INTERNAL_SERVER_ERROR.value,
            detail="Database not available",
        )
    if not await redis_health_check():
        raise HTTPException(
            status_code=CODE.INTERNAL_SERVER_ERROR.value,
            detail="Redis not available",
        )
    return BaseResponse()


@router.post("/project/profile_config", tags=["project"])
async def update_project_profile_config(
    request: Request,
    profile_config: res.ProfileConfigData = Body(
        ..., description="The profile config to update"
    ),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    if not utils.is_valid_profile_config(profile_config.profile_config):
        return Promise.reject(CODE.BAD_REQUEST, "Invalid profile config").to_response(
            BaseResponse
        )
    p = await controllers.project.update_project_profile_config(
        project_id, profile_config.profile_config
    )
    return p.to_response(res.BaseResponse)


@router.get("/project/profile_config", tags=["project"])
async def get_project_profile_config_string(
    request: Request,
) -> res.ProfileConfigDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.project.get_project_profile_config_string(project_id)
    return p.to_response(res.ProfileConfigDataResponse)


@router.post("/users", tags=["user"])
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


@router.get("/users/{user_id}", tags=["user"])
async def get_user(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to retrieve"),
) -> res.UserDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.get_user(user_id, project_id)
    return p.to_response(res.UserDataResponse)


@router.put("/users/{user_id}", tags=["user"])
async def update_user(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to update"),
    user_data: dict = Body(..., description="Updated user data"),
) -> res.IdResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.update_user(user_id, project_id, user_data)
    return p.to_response(res.IdResponse)


@router.delete("/users/{user_id}", tags=["user"])
async def delete_user(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to delete"),
) -> BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.delete_user(user_id, project_id)
    return p.to_response(BaseResponse)


@router.get("/users/blobs/{user_id}/{blob_type}", tags=["user"])
async def get_user_all_blobs(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to fetch blobs for"),
    blob_type: BlobType = Path(..., description="The type of blobs to retrieve"),
    page: int = Query(0, description="Page number for pagination, starting from 0"),
    page_size: int = Query(10, description="Number of items per page, default is 10"),
) -> res.IdsResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.get_user_all_blobs(
        user_id, project_id, blob_type, page, page_size
    )
    return p.to_response(res.IdsResponse)


@router.post("/blobs/insert/{user_id}", tags=["blob"])
async def insert_blob(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to insert the blob for"),
    blob_data: res.BlobData = Body(..., description="The blob data to insert"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> res.IdResponse:
    project_id = request.state.memobase_project_id
    background_tasks.add_task(
        capture_int_key, TelemetryKeyName.insert_blob_request, project_id=project_id
    )
    today_token_costs = await asyncio.gather(
        get_int_key(TelemetryKeyName.llm_input_tokens, project_id),
        get_int_key(TelemetryKeyName.llm_output_tokens, project_id),
    )
    p = await get_project_status(project_id)
    if not p.ok():
        return p.to_response(res.IdResponse)
    status = p.data()
    if status not in USAGE_TOKEN_LIMIT_MAP:
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR, f"Invalid project status: {status}"
        ).to_response(res.IdResponse)
    usage_token_limit = USAGE_TOKEN_LIMIT_MAP[status]
    if usage_token_limit >= 0 and (usage_token_limit < sum(today_token_costs)):
        return Promise.reject(
            CODE.SERVICE_UNAVAILABLE,
            f"Your project reaches Memobase token limit today. "
            f"quota: {usage_token_limit}, used: {sum(today_token_costs)}. "
            "\nhttps://www.memobase.io/en/pricing for more information.",
        ).to_response(res.IdResponse)

    p = await controllers.blob.insert_blob(user_id, project_id, blob_data)
    if not p.ok():
        return p.to_response(res.IdResponse)

    # TODO if single user insert too fast will cause random order insert to buffer
    # So no background task for insert buffer yet
    pb = await controllers.buffer.insert_blob_to_buffer(
        user_id, project_id, p.data().id, blob_data.to_blob()
    )
    if not pb.ok():
        return pb.to_response(res.IdResponse)

    background_tasks.add_task(
        capture_int_key,
        TelemetryKeyName.insert_blob_success_request,
        project_id=project_id,
    )
    return p.to_response(res.IdResponse)


@router.get("/blobs/{user_id}/{blob_id}", tags=["blob"])
async def get_blob(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    blob_id: str = Path(..., description="The ID of the blob to retrieve"),
) -> res.BlobDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.blob.get_blob(user_id, project_id, blob_id)
    return p.to_response(res.BlobDataResponse)


@router.delete("/blobs/{user_id}/{blob_id}", tags=["blob"])
async def delete_blob(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    blob_id: str = Path(..., description="The ID of the blob to delete"),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.blob.remove_blob(user_id, project_id, blob_id)
    return p.to_response(res.BaseResponse)


@router.get("/users/profile/{user_id}", tags=["profile"])
async def get_user_profile(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to get profiles for"),
    topk: int = Query(
        None, description="Number of profiles to retrieve, default is all"
    ),
    max_length: int = Query(
        None,
        description="Max Character length of total profile content, default is all",
    ),
) -> res.UserProfileResponse:
    """Get the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    p = await controllers.profile.get_user_profiles(user_id, project_id)
    p = await controllers.profile.truncate_profiles(
        p.data(), topk=topk, max_length=max_length
    )
    return p.to_response(res.UserProfileResponse)


@router.post("/users/buffer/{user_id}/{buffer_type}", tags=["buffer"])
async def flush_buffer(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    buffer_type: BlobType = Path(..., description="The type of buffer to flush"),
) -> res.BaseResponse:
    """Get the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    p = await controllers.buffer.wait_insert_done_then_flush(
        user_id, project_id, buffer_type
    )
    return p.to_response(res.BaseResponse)


@router.delete("/users/profile/{user_id}/{profile_id}", tags=["profile"])
async def delete_user_profile(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    profile_id: str = Path(..., description="The ID of the profile to delete"),
) -> res.BaseResponse:
    """Get the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    p = await controllers.profile.delete_user_profile(user_id, project_id, profile_id)
    return p.to_response(res.IdResponse)


@router.get("/users/event/{user_id}", tags=["event"])
async def get_user_events(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    topk: int = Query(10, description="Number of events to retrieve, default is 10"),
) -> res.UserEventsDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event.get_user_events(user_id, project_id, topk=topk)
    return p.to_response(res.UserEventsDataResponse)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not request.url.path.startswith("/api"):
            return await call_next(request)
        if request.url.path.startswith("/api/v1/healthcheck"):
            telemetry_manager.increment_counter_metric(CounterMetricName.HEALTHCHECK, 1, {"source_ip": request.client.host})
            return await call_next(request)
        auth_token = request.headers.get("Authorization")
        if not auth_token or not auth_token.startswith("Bearer "):
            return JSONResponse(
                status_code=CODE.UNAUTHORIZED.value,
                content=BaseResponse(
                    errno=CODE.UNAUTHORIZED.value,
                    errmsg=f"Unauthorized access to {request.url.path}. You have to provide a valid Bearer token.",
                ).model_dump(),
            )
        auth_token = (auth_token.split(" ")[1]).strip()
        is_root = self.is_valid_root(auth_token)
        request.state.is_memobase_root = is_root
        request.state.memobase_project_id = DEFAULT_PROJECT_ID
        if not is_root:
            p = await self.parse_project_token(auth_token)
            if not p.ok():
                return JSONResponse(
                    status_code=CODE.UNAUTHORIZED.value,
                    content=BaseResponse(
                        errno=CODE.UNAUTHORIZED.value,
                        errmsg=f"Unauthorized access to {request.url.path}. {p.msg()}",
                    ).model_dump(),
                )
            request.state.memobase_project_id = p.data()
        # await capture_int_key(TelemetryKeyName.has_request)
        telemetry_manager.increment_counter_metric(
            CounterMetricName.REQUEST,
            1,
            {
                "project_id": request.state.memobase_project_id,
                "source_ip": request.client.host,
                "path": request.url.path,
                "method": request.method,
             },
        )
        start_time = time.time()
        response = await call_next(request)
        telemetry_manager.record_histogram_metric(
            HistogramMetricName.REQUEST_LATENCY_MS,
            (time.time() - start_time) * 1000,
            {
                "project_id": request.state.memobase_project_id,
                "source_ip": request.client.host,
                "path": request.url.path,
                "method": request.method,
            },
        )
        return response

    def is_valid_root(self, token: str) -> bool:
        access_token = os.getenv("ACCESS_TOKEN")
        if access_token is None:
            return True
        return token == access_token.strip()

    async def parse_project_token(self, token: str) -> Promise[str]:
        p = parse_project_id(token)
        if not p.ok():
            return Promise.reject(CODE.UNAUTHORIZED, "Invalid project id format")
        project_id = p.data()
        p = await check_project_secret(project_id, token)
        if not p.ok():
            return p
        if not p.data():
            return Promise.reject(CODE.UNAUTHORIZED, "Wrong secret key")
        p = await get_project_status(project_id)
        if not p.ok():
            return p
        if p.data() == ProjectStatus.suspended:
            return Promise.reject(CODE.FORBIDDEN, "Your project is suspended!")
        return Promise.resolve(project_id)


app.include_router(router)
app.add_middleware(AuthMiddleware)
