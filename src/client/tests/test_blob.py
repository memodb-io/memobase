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
