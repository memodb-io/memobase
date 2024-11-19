from datetime import datetime
from ..connectors import get_redis_client


def date_key():
    return datetime.now().strftime("%Y-%m-%d")


def capture_int_key(name, value: int = 1):
    key = f"memobase_dashboard::{name}:{date_key()}"
    r_c = get_redis_client()
    r_c.incrby(key, value)
