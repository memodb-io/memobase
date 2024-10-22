import pytest
from memobase import MemoBaseClient
from memobase.error import ServerError


@pytest.fixture(scope="session")
def api_client():
    client = MemoBaseClient(
        project_url="http://localhost:8000/",
        api_key="secret",
    )
    if not client.ping():
        return pytest.skip("API not available")
    return client
