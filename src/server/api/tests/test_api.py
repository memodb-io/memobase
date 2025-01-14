import os
import pytest
from unittest.mock import patch, Mock, AsyncMock
from api import app
from fastapi.testclient import TestClient
from memobase_server import controllers
from memobase_server.models.blob import BlobType

PREFIX = "/api/v1"
TOKEN = os.getenv("ACCESS_TOKEN")


@pytest.fixture
def client():
    c = TestClient(app)
    c.headers.update({"Authorization": f"Bearer {TOKEN}"})
    return c


def test_health_check(client, db_env):
    response = client.get(f"{PREFIX}/healthcheck")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0


@pytest.fixture
def mock_llm_complete():
    with patch("memobase_server.controllers.modal.chat.llm_complete") as mock_llm:
        mock_client1 = AsyncMock()
        mock_client1.ok = Mock(return_value=True)
        mock_client1.data = Mock(return_value="- basic_info::name::Gus")

        mock_llm.side_effect = [mock_client1]
        yield mock_llm


def test_user_api_curd(client, db_env):
    response = client.post(f"{PREFIX}/users", json={"data": {"test": 1}})
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    u_id = d["data"]["id"]

    response = client.get(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    assert d["data"]["data"]["test"] == 1

    response = client.put(f"{PREFIX}/users/{u_id}", json={"data": {"test": 2}})
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0

    response = client.get(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert d["data"]["data"]["test"] == 2

    response = client.delete(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0

    response = client.get(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] != 0
    print(d)


def test_user_create_with_id(client, db_env):
    import uuid
    from time import time

    fake_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"test{time()}"))
    print(fake_id)
    response = client.post(f"{PREFIX}/users", json={"data": {"test": 1}, "id": fake_id})
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    u_id = d["data"]["id"]
    assert u_id == fake_id

    response = client.delete(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0


def test_blob_api_curd(client, db_env):
    response = client.post(f"{PREFIX}/users", json={})
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    u_id = d["data"]["id"]

    response = client.post(
        f"{PREFIX}/blobs/insert/{u_id}",
        json={
            "blob_type": "doc",
            "blob_data": {"content": "Hello world"},
            "fields": {"from": "happy"},
        },
    )
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    b_id = d["data"]["id"]

    response = client.get(f"{PREFIX}/blobs/{u_id}/{b_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    assert d["data"]["blob_type"] == "doc"
    assert d["data"]["blob_data"]["content"] == "Hello world"
    assert d["data"]["fields"]["from"] == "happy"

    client.post(
        f"{PREFIX}/blobs/insert/{u_id}",
        json={
            "blob_type": "doc",
            "blob_data": {"content": "Hello world"},
            "fields": {"from": "happy"},
        },
    )
    response = client.get(
        f"{PREFIX}/users/blobs/{u_id}/{BlobType.doc}?page=0&page_size=1"
    )
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    assert len(d["data"]["ids"]) == 1

    response = client.get(
        f"{PREFIX}/users/blobs/{u_id}/{BlobType.doc}?page=0&page_size=2"
    )
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    assert len(d["data"]["ids"]) == 2

    response = client.delete(f"{PREFIX}/blobs/{u_id}/{b_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0

    response = client.get(f"{PREFIX}/blobs/{u_id}/{b_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] != 0
    print(d)

    response = client.delete(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0


@pytest.mark.asyncio
async def test_api_user_profile(client, db_env):
    response = client.post(f"{PREFIX}/users", json={"data": {"test": 1}})
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    u_id = d["data"]["id"]

    _profiles = ["user likes to play basketball", "user is a junior school student"]
    _attributes = [
        {"topic": "interest", "sub_topic": "sports"},
        {"topic": "education", "sub_topic": "level"},
    ]
    p = await controllers.profile.add_user_profiles(u_id, _profiles, _attributes)
    assert p.ok()

    response = client.get(f"{PREFIX}/users/profile/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    assert len(d["data"]["profiles"]) == 2
    assert [dp["content"] for dp in d["data"]["profiles"]] == _profiles
    assert [dp["attributes"] for dp in d["data"]["profiles"]] == _attributes
    id1, id2 = d["data"]["profiles"][0]["id"], d["data"]["profiles"][1]["id"]

    response = client.delete(f"{PREFIX}/users/profile/{u_id}/{id1}")
    d = response.json()
    assert response.status_code == 200

    response = client.get(f"{PREFIX}/users/profile/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    assert len(d["data"]["profiles"]) == 1
    assert d["data"]["profiles"][0]["id"] == id2

    response = client.delete(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0


@pytest.mark.asyncio
async def test_api_user_flush_buffer(client, db_env, mock_llm_complete):
    response = client.post(f"{PREFIX}/users", json={"data": {"test": 1}})
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    u_id = d["data"]["id"]

    p = await controllers.buffer.get_buffer_capacity(u_id, BlobType.chat)
    assert p.ok() and p.data() == 0

    response = client.post(
        f"{PREFIX}/blobs/insert/{u_id}",
        json={
            "blob_type": "chat",
            "blob_data": {
                "messages": [
                    {"role": "user", "content": "hello, I'm Gus"},
                    {"role": "assistant", "content": "hi"},
                ]
            },
        },
    )
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    p = await controllers.buffer.get_buffer_capacity(u_id, BlobType.chat)
    assert p.ok() and p.data() == 1

    p = client.post(f"{PREFIX}/users/buffer/{u_id}/chat")
    p = await controllers.buffer.get_buffer_capacity(u_id, BlobType.chat)
    assert p.ok() and p.data() == 0

    response = client.get(f"{PREFIX}/users/profile/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    assert len(d["data"]["profiles"]) == 1
    assert [dp["content"] for dp in d["data"]["profiles"]] == ["Gus"]

    response = client.delete(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
