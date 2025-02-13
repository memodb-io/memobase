from hashlib import sha256
from datetime import datetime
from random import random
from typing import Tuple
from uuid import uuid4
from ..models.utils import Promise
from ..models.response import CODE
from ..connectors import get_redis_client
from ..controllers import project


def parse_project_id(secret_key: str) -> Promise[str]:
    if not secret_key.startswith("sk-"):
        return Promise.reject(CODE.UNAUTHORIZED, "Invalid secret key")
    parts = secret_key[3:].split("-")
    if len(parts) < 2:
        return Promise.reject(CODE.UNAUTHORIZED, "Invalid secret key")
    project_id = "-".join(parts[:-1]).strip()
    return Promise.resolve(project_id)


def token_redis_key(project_id: str) -> str:
    return f"memobase::auth::token::{project_id}"


def project_status_redis_key(project_id: str) -> str:
    return f"memobase::auth::project_status::{project_id}"


async def check_project_secret(project_id: str, secret_key: str) -> Promise[bool]:
    async with get_redis_client() as client:
        secret = await client.get(token_redis_key(project_id))
        if secret is None:
            p = await project.get_project_secret(project_id)
            if not p.ok():
                return Promise.reject(CODE.UNAUTHORIZED, "Your project is not exists!")
            secret = p.data()
            await client.set(token_redis_key(project_id), secret, ex=None)
    return Promise.resolve(secret == secret_key)


async def get_project_status(project_id: str) -> Promise[str]:
    async with get_redis_client() as client:
        status = await client.get(project_status_redis_key(project_id))
        if status is None:
            p = await project.get_project_status(project_id)
            if not p.ok():
                return p
            status = p.data()
            await client.set(
                project_status_redis_key(project_id), status.strip(), ex=60 * 60
            )
    return Promise.resolve(status)
