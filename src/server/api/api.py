import memobase_server.env
import os

# Done setting up env

from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from memobase_server.connectors import (
    close_connection,
    init_redis_pool,
)
from memobase_server import api_layer
from memobase_server.env import LOG
from uvicorn.config import LOGGING_CONFIG
from api_docs import API_X_CODE_DOCS


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_redis_pool()
    LOG.info(f"Start Memobase Server {memobase_server.__version__} 🖼️")
    yield
    await close_connection()


app = FastAPI(
    lifespan=lifespan,
)

# CORS - Allow requests from ANY origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    servers: list = []
    extra_hosts_str = os.environ.get("API_EXTRA_HOSTS")
    if extra_hosts_str:
        extra_hosts = [host.strip() for host in extra_hosts_str.split(",")]
        for host in extra_hosts:
            servers.append({"url": host})

    servers.extend(
        [
            {"url": "https://api.memobase.dev"},
            {"url": "https://api.memobase.cn"},
        ]
    )

    openapi_schema = get_openapi(
        title="Memobase API",
        version=memobase_server.__version__,
        summary="APIs for Memobase, a user memory system for LLM Apps",
        routes=app.routes,
        servers=servers,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

router = APIRouter(prefix="/api/v1")
LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
    "%(levelprefix)s %(asctime)s %(message)s"
)
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
    "%(levelprefix)s %(asctime)s %(message)s"
)
LOGGING_CONFIG["formatters"]["access"]["fmt"] = (
    "%(levelprefix)s %(asctime)s %(client_addr)s - %(request_line)s %(status_code)s"
)
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"


router.get(
    "/healthcheck", tags=["chore"], openapi_extra=API_X_CODE_DOCS["GET /healthcheck"]
)(api_layer.chore.healthcheck)


router.post(
    "/project/profile_config",
    tags=["project"],
    openapi_extra=API_X_CODE_DOCS["POST /project/profile_config"],
)(api_layer.project.update_project_profile_config)

router.get(
    "/project/profile_config",
    tags=["project"],
    openapi_extra=API_X_CODE_DOCS["GET /project/profile_config"],
)(api_layer.project.get_project_profile_config_string)


router.get("/project/billing", tags=["project"])(api_layer.project.get_project_billing)


router.post(
    "/users",
    tags=["user"],
    openapi_extra=API_X_CODE_DOCS["POST /users"],
)(api_layer.user.create_user)


router.get(
    "/users/{user_id}",
    tags=["user"],
    openapi_extra=API_X_CODE_DOCS["GET /users/{user_id}"],
)(api_layer.user.get_user)


router.put(
    "/users/{user_id}",
    tags=["user"],
    openapi_extra=API_X_CODE_DOCS["PUT /users/{user_id}"],
)(api_layer.user.update_user)

router.delete(
    "/users/{user_id}",
    tags=["user"],
    openapi_extra=API_X_CODE_DOCS["DELETE /users/{user_id}"],
)(api_layer.user.delete_user)


router.get(
    "/users/blobs/{user_id}/{blob_type}",
    tags=["user"],
    openapi_extra=API_X_CODE_DOCS["GET /users/blobs/{user_id}/{blob_type}"],
)(api_layer.user.get_user_all_blobs)


router.post(
    "/blobs/insert/{user_id}",
    tags=["blob"],
    openapi_extra=API_X_CODE_DOCS["POST /blobs/insert/{user_id}"],
)(api_layer.blob.insert_blob)


router.get(
    "/blobs/{user_id}/{blob_id}",
    tags=["blob"],
    openapi_extra=API_X_CODE_DOCS["GET /blobs/{user_id}/{blob_id}"],
)(api_layer.blob.get_blob)


router.delete(
    "/blobs/{user_id}/{blob_id}",
    tags=["blob"],
    openapi_extra=API_X_CODE_DOCS["DELETE /blobs/{user_id}/{blob_id}"],
)(api_layer.blob.delete_blob)


router.get(
    "/users/profile/{user_id}",
    tags=["profile"],
    openapi_extra=API_X_CODE_DOCS["GET /users/profile/{user_id}"],
)(api_layer.profile.get_user_profile)

router.post(
    "/users/profile/{user_id}",
    tags=["profile"],
    openapi_extra=API_X_CODE_DOCS["POST /users/profile/{user_id}"],
)(api_layer.profile.add_user_profile)

router.put(
    "/users/profile/{user_id}/{profile_id}",
    tags=["profile"],
    openapi_extra=API_X_CODE_DOCS["PUT /users/profile/{user_id}/{profile_id}"],
)(api_layer.profile.update_user_profile)

router.delete(
    "/users/profile/{user_id}/{profile_id}",
    tags=["profile"],
    openapi_extra=API_X_CODE_DOCS["DELETE /users/profile/{user_id}/{profile_id}"],
)(api_layer.profile.delete_user_profile)

router.post(
    "/users/buffer/{user_id}/{buffer_type}",
    tags=["buffer"],
    openapi_extra=API_X_CODE_DOCS["POST /users/buffer/{user_id}/{buffer_type}"],
)(api_layer.buffer.flush_buffer)

router.get(
    "/users/event/{user_id}",
    tags=["event"],
    openapi_extra=API_X_CODE_DOCS["GET /users/event/{user_id}"],
)(api_layer.event.get_user_events)


router.get(
    "/users/context/{user_id}",
    tags=["context"],
    openapi_extra=API_X_CODE_DOCS["GET /users/context/{user_id}"],
)(api_layer.context.get_user_context)


app.include_router(router)
app.add_middleware(api_layer.middleware.AuthMiddleware)
