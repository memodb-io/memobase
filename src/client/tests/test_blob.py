import pytest
from memobase.core.blob import DocBlob, ChatBlob
from memobase.error import ServerError
from memobase.core.blob import BlobType


def test_blob_curd_client(api_client):
    a = api_client
    blob = DocBlob(content="test", fields={"1": "fool"})
    u = a.add_user()
    print(u)
    ud = a.get_user(u)

    b = ud.insert(blob)
    print(ud.get(b))
    print(ud.delete(b))
    with pytest.raises(ServerError):
        ud.get(b)


def test_blob_get_all(api_client):
    a = api_client
    blob = DocBlob(content="test", fields={"1": "fool"})
    u = a.add_user()
    print(u)
    ud = a.get_user(u)

    b = ud.insert(blob)
    b = ud.insert(blob)
    b = ud.insert(blob)
    b = ud.insert(blob)
    r = ud.get_all(BlobType.doc)
    print(ud.delete(b))
    assert len(r) == 4
    with pytest.raises(ServerError):
        ud.get(b)
    a.delete_user(u)


def test_flush_curd_client(api_client):
    mb = api_client
    uid = mb.add_user({"me": "test"})
    u = mb.get_user(uid)
    print(u.profile(need_json=True))
    u.insert(
        ChatBlob(
            messages=[
                {
                    "role": "user",
                    "content": "Hello, I'm Gus",
                },
                {
                    "role": "assistant",
                    "content": "Hi, nice to meet you, Gus!",
                },
            ]
        )
    )
    u.flush()
    ps = u.profile()
    print(u.profile(need_json=True))
    print([p.describe for p in ps])
    print(u.event())
    mb.delete_user(uid)
    print("Deleted user")


def test_blob_to_request_created_at():
    from datetime import datetime

    timestamp = datetime(2025, 9, 1, 12, 0, 0)
    blob_with_time = ChatBlob(
        messages=[{"role": "user", "content": "Hi"}],
        created_at=timestamp,
    )
    req = blob_with_time.to_request()
    assert req["created_at"] == timestamp.isoformat()
    assert req["blob_type"] == BlobType.chat

    blob_without_time = DocBlob(content="Hello world")
    req_without = blob_without_time.to_request()
    assert "created_at" not in req_without
    assert req_without["blob_type"] == BlobType.doc
