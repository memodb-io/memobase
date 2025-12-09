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
from memobase_server.llms.embeddings import check_embedding_sanity
from memobase_server.llms import llm_sanity_check
from memobase_server.api_layer.docs import API_X_CODE_DOCS
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_redis_pool()
    await check_embedding_sanity()
    await llm_sanity_check()
    LOG.info(f"Start Memobase Server {memobase_server.__version__} 🖼️")
    yield
    await close_connection()


app = FastAPI(
    lifespan=lifespan,
)

# CORS configuration
USE_CORS = os.environ.get("USE_CORS", "False").lower() == "true"  # Default to False
API_HOSTS_STR = os.environ.get(
    "API_HOSTS", "https://api.memobase.dev,https://api.memobase.cn"
)
API_HOSTS = [host.strip() for host in API_HOSTS_STR.split(",")]

if USE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=API_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

NO_AUTH = {"/api/v1/healthcheck"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    servers: list = []
    for host in API_HOSTS:
        servers.append({"url": host})

    openapi_schema = get_openapi(  # type: ignore
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
    for path in openapi_schema["paths"]:
        if path in NO_AUTH:
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = []

    app.openapi_schema = openapi_schema  # type: ignore
    return app.openapi_schema


app.openapi = custom_openapi


router = APIRouter(prefix="/api/v1")


router.get(
    "/healthcheck", tags=["chore"], openapi_extra=API_X_CODE_DOCS["GET /healthcheck"]
)(api_layer.chore.healthcheck)

router.get(
    "/admin/status_check",
    tags=["admin"],
    # openapi_extra=API_X_CODE_DOCS["GET /admin/status_check"],
)(api_layer.chore.root_running_status_check)

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


router.get(
    "/project/billing",
    tags=["project"],
    openapi_extra=API_X_CODE_DOCS["GET /project/billing"],
)(api_layer.project.get_project_billing)


router.get(
    "/project/users",
    tags=["project"],
    openapi_extra=API_X_CODE_DOCS["GET /project/users"],
)(api_layer.project.get_project_users)


router.get(
    "/project/usage",
    tags=["project"],
    openapi_extra=API_X_CODE_DOCS["GET /project/usage"],
)(api_layer.project.get_project_usage)


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

router.post(
    "/users/profile/import/{user_id}",
    tags=["profile"],
)(api_layer.profile.import_user_context)

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
    "/users/buffer/capacity/{user_id}/{buffer_type}",
    tags=["buffer"],
    openapi_extra=API_X_CODE_DOCS["GET /users/buffer/capacity/{user_id}/{buffer_type}"],
)(api_layer.buffer.get_processing_buffer_ids)

router.get(
    "/users/event/{user_id}",
    tags=["event"],
    openapi_extra=API_X_CODE_DOCS["GET /users/event/{user_id}"],
)(api_layer.event.get_user_events)

router.put(
    "/users/event/{user_id}/{event_id}",
    tags=["event"],
    openapi_extra=API_X_CODE_DOCS["PUT /users/event/{user_id}/{event_id}"],
)(api_layer.event.update_user_event)

router.delete(
    "/users/event/{user_id}/{event_id}",
    tags=["event"],
    openapi_extra=API_X_CODE_DOCS["DELETE /users/event/{user_id}/{event_id}"],
)(api_layer.event.delete_user_event)

router.get(
    "/users/event/search/{user_id}",
    tags=["event"],
    openapi_extra=API_X_CODE_DOCS["GET /users/event/search/{user_id}"],
)(api_layer.event.search_user_events)

router.get(
    "/users/event_gist/search/{user_id}",
    tags=["event_gist"],
    openapi_extra=API_X_CODE_DOCS["GET /users/event_gist/search/{user_id}"],
)(api_layer.event.search_user_event_gists)

router.get(
    "/users/event_tags/search/{user_id}",
    tags=["event"],
    openapi_extra=API_X_CODE_DOCS["GET /users/event_tags/search/{user_id}"],
)(api_layer.event.search_user_events_by_tags)

router.get(
    "/users/context/{user_id}",
    tags=["context"],
    openapi_extra=API_X_CODE_DOCS["GET /users/context/{user_id}"],
)(api_layer.context.get_user_context)


router.post(
    "/users/roleplay/proactive/{user_id}",
    tags=["roleplay"],
    # openapi_extra=API_X_CODE_DOCS["POST /users/roleplay/proactive/{user_id}"],
)(api_layer.roleplay.infer_proactive_topics)


@app.middleware("http")
async def global_wrapper_middleware(request, call_next):
    return await api_layer.middleware.global_wrapper_middleware(request, call_next)


app.include_router(router)
app.add_middleware(api_layer.middleware.AuthMiddleware)

FastAPIInstrumentor.instrument_app(app)
