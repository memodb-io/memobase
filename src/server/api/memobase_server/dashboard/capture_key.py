from datetime import datetime
from ..connectors import get_redis_client


def date_key():
    return datetime.now().strftime("%Y-%m-%d")


async def capture_int_key(name, value: int = 1):
    key = f"memobase_dashboard::{name}:{date_key()}"
    async with get_redis_client() as r_c:
        await r_c.incrby(key, value)


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(capture_int_key("test_key")))
