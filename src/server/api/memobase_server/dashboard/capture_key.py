from datetime import datetime
from ..connectors import get_redis_client, PROJECT_ID


def date_key():
    return datetime.now().strftime("%Y-%m-%d")


def capture_int_key(name, value: int = 1):
    key = f"memobase_dashboard::{PROJECT_ID}::{name}:{date_key()}"
    r_c = get_redis_client()
    r_c.incrby(key, value)
