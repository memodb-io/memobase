import os
import asyncio
import redis.exceptions as redis_exceptions
import redis.asyncio as redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from uuid import uuid4
from .env import LOG
from .models.database import REG, Project, UserEvent, UserEventGist

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
PROJECT_ID = os.getenv("PROJECT_ID")
ADMIN_URL = os.getenv("ADMIN_URL")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

if PROJECT_ID is None:
    LOG.warning(f"PROJECT_ID is not set")
    PROJECT_ID = "default"
LOG.info(f"Project ID: {PROJECT_ID}")
LOG.info(f"Database URL: {DATABASE_URL}")
LOG.info(f"Redis URL: {REDIS_URL}")

# Create an engine
DB_ENGINE = create_engine(
    DATABASE_URL,
    pool_size=75,  # Increased from 50 to handle more concurrent operations
    max_overflow=50,  # Increased from 30 to provide more buffer
    pool_recycle=300,  # Reduced from 600 to recycle connections more frequently
    pool_pre_ping=True,  # Verify connections before using
    pool_timeout=45,  # Increased from 30 seconds for better handling under load
    pool_reset_on_return="commit",  # Ensure clean state when connections are returned
    echo_pool=False,  # Set to True for debugging pool issues
)
REDIS_POOL = None

Session = sessionmaker(bind=DB_ENGINE)


def create_pgvector_extension():
    try:
        with Session() as session:
            session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            session.commit()
            LOG.info("pgvector extension created or already exists")
    except Exception as e:
        LOG.error(f"Failed to create pgvector extension: {e}")


def create_tables():
    create_pgvector_extension()

    REG.metadata.create_all(DB_ENGINE)
    with Session() as session:
        Project.initialize_root_project(session)
        UserEvent.check_legal_embedding_dim(session)
        UserEventGist.check_legal_embedding_dim(session)
    LOG.info("Database tables created successfully")


create_tables()


def db_health_check() -> bool:
    try:
        conn = DB_ENGINE.connect()
    except OperationalError as e:
        LOG.error(f"Database connection failed: {e}")
        return False
    else:
        conn.close()
        return True


async def redis_health_check() -> bool:
    try:
        async with get_redis_client() as redis_client:
            await redis_client.ping()
    except redis_exceptions.ConnectionError as e:
        LOG.error(f"Redis connection failed: {e}")
        return False
    else:
        return True


async def close_connection():
    DB_ENGINE.dispose()
    if REDIS_POOL is not None:
        await REDIS_POOL.aclose()
    LOG.info("Connections closed")


def init_redis_pool():
    global REDIS_POOL
    REDIS_POOL = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)


def get_redis_client() -> redis.Redis:
    if REDIS_POOL is not None:
        return redis.Redis(connection_pool=REDIS_POOL, decode_responses=True)
    else:
        return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def get_pool_status() -> dict:
    """Get current connection pool status for monitoring."""
    pool = DB_ENGINE.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_capacity": pool.size() + pool.overflow(),
        "utilization_percent": (
            round((pool.checkedout() / (pool.size() + pool.overflow())) * 100, 2)
            if (pool.size() + pool.overflow()) > 0
            else 0
        ),
    }


def log_pool_status(operation: str = "unknown"):
    """Log current pool status for debugging."""
    status = get_pool_status()
    if status["utilization_percent"] > 80:  # Log warning if utilization is high
        LOG.warning(
            f"High DB pool utilization after {operation}: "
            f"{status['checked_out']}/{status['total_capacity']} "
            f"({status['utilization_percent']}%) - "
            f"Available: {status['checked_in']}, Overflow: {status['overflow']}"
        )
    LOG.info(f"[DB pool status] {operation}: {status}")


if __name__ == "__main__":

    async def main():
        try:
            result = await redis_health_check()
            print(result)
        finally:
            await close_connection()

    asyncio.run(main())
