import os
import logging
from dotenv import load_dotenv
from memobase_server.utils import LOG

load_dotenv()

LOG.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter(
        "%(levelname)s:    %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
LOG.addHandler(console_handler)
# Done setting up env

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from memobase_server.connectors import db_health_check, redis_health_check
from memobase_server.models.response import BaseResponse, CODE
from memobase_server.models import response as res
from memobase_server import controllers

app = FastAPI()
router = APIRouter(prefix="/api/v1")


@router.get("/healthcheck")
async def healthcheck() -> BaseResponse:
    LOG.info("Healthcheck requested")
    if not db_health_check():
        raise HTTPException(
            status_code=CODE.INTERNAL_SERVER_ERROR.value,
            detail="Database not available",
        )
    if not redis_health_check():
        raise HTTPException(
            status_code=CODE.INTERNAL_SERVER_ERROR.value,
            detail="Redis not available",
        )
    return BaseResponse()


@router.post("/users")
async def create_user(user_data: res.UserData) -> res.IdResponse:
    p = await controllers.user.create_user(user_data)
    return p.to_response(res.IdResponse)


@router.get("/users/{user_id}")
async def get_user(user_id: int) -> res.UserDataResponse:
    p = await controllers.user.get_user(user_id)
    return p.to_response(res.UserDataResponse)


@router.get("/users/{user_id}")
async def get_user(user_id: int) -> res.UserDataResponse:
    p = await controllers.user.get_user(user_id)
    return p.to_response(res.UserDataResponse)


@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: res.UserData) -> res.IdResponse:
    p = await controllers.user.update_user(user_id, user_data)
    return p.to_response(res.IdResponse)


@router.delete("/users/{user_id}")
async def delete_user(user_id: int) -> BaseResponse:
    p = await controllers.user.delete_user(user_id)
    return p.to_response(BaseResponse)


@router.post("/blobs/insert/{user_id}")
async def insert_blob(user_id: int, blob_data: res.BlobData) -> res.IdResponse:
    p = await controllers.blob.insert_blob(user_id, blob_data)
    return p.to_response(res.IdResponse)


@router.get("/blobs/{user_id}/{blob_id}")
async def get_blob(user_id: int, blob_id: int) -> res.BlobDataResponse:
    p = await controllers.blob.get_blob(user_id, blob_id)
    return p.to_response(res.BlobDataResponse)


@router.delete("/blobs/{user_id}/{blob_id}")
async def delete_blob(user_id: int, blob_id: int) -> res.BaseResponse:
    p = await controllers.blob.remove_blob(user_id, blob_id)
    return p.to_response(res.BaseResponse)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
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
