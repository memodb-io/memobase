import memobase_server.env

# Done setting up env

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from memobase_server.connectors import (
    db_health_check,
    redis_health_check,
    close_connection,
    init_redis_pool,
)
from memobase_server.models.response import BaseResponse, CODE
from memobase_server.models.blob import BlobType
from memobase_server.models import response as res
from memobase_server import controllers
from memobase_server.env import LOG, TelemetryKeyName
from memobase_server.telemetry.capture_key import capture_int_key
from uvicorn.config import LOGGING_CONFIG


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_redis_pool()
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


@router.post("/users", tags=["user"])
async def create_user(user_data: res.UserData) -> res.IdResponse:
    """Create a new user with additional data"""
    p = await controllers.user.create_user(user_data)
    return p.to_response(res.IdResponse)


@router.get("/users/{user_id}", tags=["user"])
async def get_user(user_id: str) -> res.UserDataResponse:
    p = await controllers.user.get_user(user_id)
    return p.to_response(res.UserDataResponse)


@router.put("/users/{user_id}", tags=["user"])
async def update_user(user_id: str, user_data: res.UserData) -> res.IdResponse:
    p = await controllers.user.update_user(user_id, user_data)
    return p.to_response(res.IdResponse)


@router.delete("/users/{user_id}", tags=["user"])
async def delete_user(user_id: str) -> BaseResponse:
    p = await controllers.user.delete_user(user_id)
    return p.to_response(BaseResponse)


@router.post("/blobs/insert/{user_id}", tags=["user"])
async def insert_blob(
    user_id: str, blob_data: res.BlobData, background_tasks: BackgroundTasks
) -> res.IdResponse:
    background_tasks.add_task(capture_int_key, TelemetryKeyName.insert_blob_request)

    p = await controllers.blob.insert_blob(user_id, blob_data)
    if not p.ok():
        return p.to_response(res.IdResponse)

    # TODO if single user insert too fast will cause random order insert to buffer
    # So no background task for insert buffer yet
    pb = await controllers.buffer.insert_blob_to_buffer(
        user_id, p.data().id, blob_data.to_blob()
    )
    if not pb.ok():
        return pb.to_response(res.IdResponse)

    background_tasks.add_task(
        capture_int_key, TelemetryKeyName.insert_blob_success_request
    )
    return p.to_response(res.IdResponse)


@router.get("/blobs/{user_id}/{blob_id}", tags=["user"])
async def get_blob(user_id: str, blob_id: str) -> res.BlobDataResponse:
    p = await controllers.blob.get_blob(user_id, blob_id)
    return p.to_response(res.BlobDataResponse)


@router.delete("/blobs/{user_id}/{blob_id}", tags=["user"])
async def delete_blob(user_id: str, blob_id: str) -> res.BaseResponse:
    p = await controllers.blob.remove_blob(user_id, blob_id)
    return p.to_response(res.BaseResponse)


@router.get("/users/profile/{user_id}", tags=["user"])
async def get_user_profile(user_id: str) -> res.UserProfileResponse:
    """Get the real-time user profiles for long term memory"""
    p = await controllers.profile.get_user_profiles(user_id)
    return p.to_response(res.UserProfileResponse)


@router.post("/users/buffer/{user_id}/{buffer_type}", tags=["user"])
async def flush_buffer(user_id: str, buffer_type: BlobType) -> res.BaseResponse:
    """Get the real-time user profiles for long term memory"""
    p = await controllers.buffer.wait_insert_done_then_flush(user_id, buffer_type)
    return p.to_response(res.BaseResponse)


@router.delete("/users/profile/{user_id}/{profile_id}", tags=["user"])
async def delete_user_profile(user_id: str, profile_id: str) -> res.BaseResponse:
    """Get the real-time user profiles for long term memory"""
    p = await controllers.profile.delete_user_profile(user_id, profile_id)
    return p.to_response(res.IdResponse)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not request.url.path.startswith("/api"):
            return await call_next(request)
        if request.url.path.startswith("/api/v1/healthcheck"):
            return await call_next(request)
        auth_token = request.headers.get("Authorization")
        if not auth_token or not self.is_valid_token(auth_token):
            return JSONResponse(
                status_code=CODE.UNAUTHORIZED.value,
                content=BaseResponse(
                    errno=CODE.UNAUTHORIZED.value,
                    errmsg=f"Unauthorized access to {request.url.path}",
                ).model_dump(),
            )
        response = await call_next(request)
        return response

    def is_valid_token(self, token: str) -> bool:
        if not token.startswith("Bearer "):
            return False
        token = token.split(" ")[1]
        access_token = os.getenv("ACCESS_TOKEN")
        if access_token is None:
            return True
        return token == access_token


app.include_router(router)
app.add_middleware(AuthMiddleware)
