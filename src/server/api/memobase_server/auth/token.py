from hashlib import sha256
from datetime import datetime
from random import random
from typing import Tuple
from uuid import uuid4
from ..models.utils import Promise
from ..models.response import CODE
from ..connectors import get_redis_client
from ..controllers import project


def generate_project_id() -> str:
    salt = sha256(f"{uuid4()}".encode()).hexdigest()[:16]
    return f"proj-{salt}"


def generate_secret_key(project_id: str) -> str:
    # using project_id and time to generate a one-way secret key
    secret = sha256(
        f"{project_id}-{datetime.now().timestamp()}-{random()}".encode()
    ).hexdigest()[:32]
    assert "-" not in secret
    return f"sk-{project_id}-{secret}"


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


async def set_project_secret(project_id: str, secret_key: str) -> Promise[None]:
    p = await project.update_project_secret(project_id, secret_key)
    if not p.ok():
        return p
    async with get_redis_client() as client:
        await client.set(token_redis_key(project_id), secret_key.strip(), ex=None)
    return Promise.resolve(None)


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


async def get_project_secret(project_id: str) -> Promise[str]:
    async with get_redis_client() as client:
        secret = await client.get(token_redis_key(project_id))
        if secret is None:
            p = await project.get_project_secret(project_id)
            if not p.ok():
                return Promise.reject(CODE.UNAUTHORIZED, "Your project is not exists!")
            secret = p.data()
            await client.set(token_redis_key(project_id), secret, ex=None)
    return Promise.resolve(secret)


async def delete_project_secret(project_id: str) -> Promise[None]:
    async with get_redis_client() as client:
        await client.delete(token_redis_key(project_id))
    return Promise.resolve(None)
