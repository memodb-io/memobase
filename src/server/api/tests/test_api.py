import os
import pytest
from api import app
from fastapi.testclient import TestClient
from memobase_server import controllers

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
    p = await controllers.user.add_user_profiles(
        u_id,
        _profiles,
        _attributes,
        [[] for _ in range(len(_attributes))],
    )
    assert p.ok()

    response = client.get(f"{PREFIX}/users/profile/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
    assert len(d["data"]["profiles"]) == 2
    assert [dp["content"] for dp in d["data"]["profiles"]] == _profiles
    assert [dp["attributes"] for dp in d["data"]["profiles"]] == _attributes

    response = client.delete(f"{PREFIX}/users/{u_id}")
    d = response.json()
    assert response.status_code == 200
    assert d["errno"] == 0
