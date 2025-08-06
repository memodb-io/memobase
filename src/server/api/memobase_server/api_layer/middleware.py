import os
import time
import uuid
import structlog
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from uvicorn.protocols.utils import get_path_with_query_string
from ..env import ProjectStatus, LOG
from ..models.database import DEFAULT_PROJECT_ID
from ..models.response import BaseResponse
from ..models.utils import Promise
from ..telemetry import (
    telemetry_manager,
    CounterMetricName,
    HistogramMetricName,
)
from .. import __version__
from ..models.response import BaseResponse, CODE
from ..auth.token import (
    parse_project_id,
    check_project_secret,
    get_project_status,
)


PATH_MAPPINGS = [
    "/api/v1/admin/status_check",
    "/api/v1/users/blobs",
    "/api/v1/users/blobs",
    "/api/v1/users/profile",
    "/api/v1/users/buffer",
    "/api/v1/users/event",
    "/api/v1/users/context",
    "/api/v1/users",
    "/api/v1/blobs/insert",
    "/api/v1/blobs",
]


async def global_wrapper_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID")
    if req_id is None:
        req_id = str(uuid.uuid4())
    project_id = getattr(request.state, "memobase_project_id", None)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=req_id, project_id=project_id, memobase_version=__version__
    )

    url = get_path_with_query_string(request.scope)
    client_host = request.client.host
    client_port = request.client.port
    http_method = request.method
    http_version = request.scope["http_version"]

    start_time = time.perf_counter_ns()

    try:
        response = await call_next(request)
        status_code = response.status_code
        errmsg = None
        traceback_str = None
    except Exception as e:
        status_code = 500
        errmsg = f"Sorry, we have encountered an unknown error: \n{e}\nPlease report this issue to https://github.com/memodb-io/memobase/issues"
        traceback_str = traceback.format_exc().replace("\n", "<br>")
        response = JSONResponse(
            content={
                "data": None,
                "errno": 500,
                "errmsg": errmsg,
            },
        )
    process_time = time.perf_counter_ns() - start_time

    if status_code != 200:
        _log_f = LOG.error
    else:
        _log_f = LOG.info
    _log_f(
        f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
        extra={
            "http": {
                "url": str(request.url),
                "status_code": status_code,
                "method": http_method,
                "version": http_version,
            },
            "network": {"client": {"ip": client_host, "port": client_port}},
            "duration": process_time / 10**9,  # convert to s
            "type": "access",
            "errmsg": errmsg,
            "__internal_traceback": traceback_str,
        },
    )
    response.headers["X-Process-Time"] = str(process_time / 10**9)

    return response


class AuthMiddleware(BaseHTTPMiddleware):
    def normalize_path(self, path: str) -> str:
        """Remove dynamic path parameters to get normalized path for metrics"""
        if not path.startswith("/api"):
            return path

        for prefix in PATH_MAPPINGS:
            if path.startswith(prefix):
                return prefix

        return path

    async def dispatch(self, request, call_next):
        if not request.url.path.startswith("/api"):
            return await call_next(request)

        if request.url.path.startswith("/api/v1/healthcheck"):
            telemetry_manager.increment_counter_metric(
                CounterMetricName.HEALTHCHECK,
                1,
            )
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

        normalized_path = self.normalize_path(request.url.path)

        telemetry_manager.increment_counter_metric(
            CounterMetricName.REQUEST,
            1,
            {
                "project_id": request.state.memobase_project_id,
                "path": normalized_path,
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
                "path": normalized_path,
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
