from datetime import datetime
from ..connectors import get_redis_client, PROJECT_ID


def date_key():
    return datetime.now().strftime("%Y-%m-%d")


def head_key():
    return f"memobase_telemetry::{PROJECT_ID}"


async def capture_int_key(name, value: int = 1, expire_days: int = 14):
    key = f"{head_key()}::{name}::{date_key()}"
    async with get_redis_client() as r_c:
        await r_c.incrby(key, value)
        await r_c.expire(key, expire_days * 24 * 60 * 60)


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(capture_int_key("test_key")))
