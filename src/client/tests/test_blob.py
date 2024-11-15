import pytest
from memobase.core.blob import DocBlob, ChatBlob
from memobase.error import ServerError


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


def test_flush_curd_client(api_client):
    mb = api_client
    uid = mb.add_user({"me": "test"})
    u = mb.get_user(uid)
    print(u.profile())
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
    print([p.describe for p in ps])
    mb.delete_user(uid)
    print("Deleted user")
