import pytest
from time import time
from memobase.error import ServerError
from memobase.utils import string_to_uuid
from memobase.core.blob import ChatBlob

CONFIG = """
language: zh
"""


@pytest.mark.asyncio
async def test_user_curd_async_client(api_async_client):
    a = api_async_client

    print(await api_async_client.get_config())
    print(await api_async_client.update_config(CONFIG))
    c = await api_async_client.get_config()
    assert c == CONFIG

    u = await a.add_user()
    print(u)
    ud = await a.get_user(u)
    print(await a.update_user(u, {"test": 111}))
    print("user", ud.fields)
    print(await a.delete_user(u))
    with pytest.raises(ServerError):
        await a.get_user(u)

    new_uid = string_to_uuid(f"test{time()}")
    ud = await a.get_or_create_user(new_uid)
    assert ud.user_id == new_uid


@pytest.mark.asyncio
async def test_user_event_curd_async_client(api_async_client):
    a = api_async_client

    print(await api_async_client.get_config())
    print(await api_async_client.update_config(CONFIG))
    c = await api_async_client.get_config()
    assert c == CONFIG

    uid = await a.add_user()
    print(uid)
    u = await a.get_user(uid)

    await u.insert(
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
    await u.flush()

    ets = await u.event()
    print(ets)
    assert len(ets) == 1

    await u.update_event(ets[0].id, {"event_tip": "test"})
    ets = await u.event()
    print(ets)
    assert len(ets) == 1
    assert ets[0].event_data.event_tip == "test"

    await u.delete_event(ets[0].id)
    ets = await u.event()
    assert len(ets) == 0

    await a.delete_user(uid)
