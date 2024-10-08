import os
import redis
import redis.exceptions
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from .utils import LOG

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

LOG.info(f"Database URL: {DATABASE_URL}")
LOG.info(f"Redis URL: {REDIS_URL}")
# Create an engine
DB_ENGINE = create_engine(
    DATABASE_URL, pool_size=20, pool_recycle=3600, pool_pre_ping=True
)
REDIS_POOL = redis.ConnectionPool.from_url(REDIS_URL)

Session = sessionmaker(bind=DB_ENGINE)


def db_health_check() -> bool:
    try:
        conn = DB_ENGINE.connect()
    except OperationalError as e:
        LOG.error(f"Database connection failed: {e}")
        return False
    else:
        conn.close()
        return True


def redis_health_check() -> bool:
    try:
        redis_client = get_redis_client()
        redis_client.ping()
    except redis.exceptions.ConnectionError as e:
        LOG.error(f"Redis connection failed: {e}")
        return False
    else:
        return True


def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=REDIS_POOL)
