import pytest
from memobase.error import ServerError


def test_user_curd_client(api_client):
    a = api_client
    u = a.add_user()
    print(u)
    ud = a.get_user(u)
    print(a.update_user(u, {"test": 111}))
    print("user", a.get_user(u).fields)
    print(a.delete_user(u))
    with pytest.raises(ServerError):
        a.get_user(u)
