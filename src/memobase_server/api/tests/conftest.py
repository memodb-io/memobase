import pytest
from memobase_server.connectors import (
    db_health_check,
    redis_health_check,
)


def db_connection():
    return db_health_check() and redis_health_check()


@pytest.fixture(scope="session")
def db_env():
    assert db_connection() == True
    yield
    print("Tearing down the environment...")
