import pytest
from memobase_server import controllers
from memobase_server.models import response as res
from memobase_server.models.blob import BlobType
from memobase_server.models.database import DEFAULT_PROJECT_ID


@pytest.mark.asyncio
async def test_user_curd(db_env):
    p = await controllers.user.create_user(
        res.UserData(data={"test": 1}), DEFAULT_PROJECT_ID
    )
    assert p.ok()
    d = p.data()
    u_id = d.id

    p = await controllers.user.get_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
    d = p.data().data
    assert d["test"] == 1

    p = await controllers.user.update_user(u_id, DEFAULT_PROJECT_ID, {"test": 2})
    assert p.ok()
    p = await controllers.user.get_user(u_id, DEFAULT_PROJECT_ID)
    assert p.data().data["test"] == 2

    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
    p = await controllers.user.get_user(u_id, DEFAULT_PROJECT_ID)
    assert not p.ok()


@pytest.mark.asyncio
async def test_blob_curd(db_env):
    p = await controllers.user.create_user(res.UserData(), DEFAULT_PROJECT_ID)
    assert p.ok()
    u_id = p.data().id

    p = await controllers.blob.insert_blob(
        u_id,
        DEFAULT_PROJECT_ID,
        res.BlobData(
            blob_type=BlobType.doc,
            blob_data={"content": "Hello world"},
            fields={"from": "happy"},
        ),
    )
    assert p.ok()
    b_id = p.data().id

    p = await controllers.blob.get_blob(u_id, DEFAULT_PROJECT_ID, b_id)
    assert p.ok()
    d = p.data()
    assert d.blob_type == BlobType.doc
    assert d.blob_data["content"] == "Hello world"
    assert d.fields["from"] == "happy"

    p = await controllers.blob.remove_blob(u_id, DEFAULT_PROJECT_ID, b_id)
    assert p.ok()
    p = await controllers.blob.get_blob(u_id, DEFAULT_PROJECT_ID, b_id)
    assert not p.ok()

    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()


@pytest.mark.asyncio
async def test_user_blob_curd(db_env):
    p = await controllers.user.create_user(res.UserData(), DEFAULT_PROJECT_ID)
    assert p.ok()
    u_id = p.data().id

    p = await controllers.blob.insert_blob(
        u_id,
        DEFAULT_PROJECT_ID,
        res.BlobData(
            blob_type=BlobType.chat,
            blob_data={
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello world",
                    },
                    {
                        "role": "assistant",
                        "content": "Hi",
                    },
                ]
            },
            fields={"from": "happy"},
        ),
    )
    assert p.ok()
    b_id = p.data().id
    p = await controllers.blob.insert_blob(
        u_id,
        DEFAULT_PROJECT_ID,
        res.BlobData(
            blob_type=BlobType.chat,
            blob_data={
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello world",
                    },
                    {
                        "role": "assistant",
                        "content": "Hi",
                    },
                ]
            },
            fields={"from": "happy"},
        ),
    )
    assert p.ok()
    b_id2 = p.data().id

    p = await controllers.user.get_user_all_blobs(
        u_id, DEFAULT_PROJECT_ID, BlobType.chat
    )
    assert p.ok()
    assert len(p.data().ids) == 2

    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()

    p = await controllers.blob.get_blob(u_id, DEFAULT_PROJECT_ID, b_id)
    assert not p.ok()
    p = await controllers.blob.get_blob(u_id, DEFAULT_PROJECT_ID, b_id2)
    assert not p.ok()

    p = await controllers.user.get_user_all_blobs(
        u_id, DEFAULT_PROJECT_ID, BlobType.chat
    )
    assert len(p.data().ids) == 0
