import pytest
import asyncio
from api import app
from memobase_server.env import CONFIG
from fastapi.testclient import TestClient

PREFIX = "/api/v1"
CONFIG.minimum_chats_token_size_for_event_summary = 5
CONFIG.event_tags = [
    {"name": "emotion", "description": "Record the current emotion of user"},
    {"name": "goal", "description": "Record the current goal of user"},
]
# @pytest.fixture(scope="session")
# def event_loop():
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="function")
async def db_env():
    client = TestClient(app)
    response = client.get(f"{PREFIX}/healthcheck")
    d = response.json()
    if response.status_code == 200 and d["errno"] == 0:
        yield
    else:
        pytest.skip("Database not available")
