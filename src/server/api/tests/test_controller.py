import pytest
from memobase_server import controllers
from memobase_server.models import response as res
from memobase_server.models.blob import BlobType


@pytest.mark.asyncio
async def test_user_curd(db_env):
    p = await controllers.user.create_user(res.UserData(data={"test": 1}))
    assert p.ok()
    d = p.data()
    u_id = d.id

    p = await controllers.user.get_user(d.id)
    assert p.ok()
    d = p.data().data
    assert d["test"] == 1

    p = await controllers.user.update_user(u_id, res.UserData(data={"test": 2}))
    assert p.ok()
    p = await controllers.user.get_user(u_id)
    assert p.data().data["test"] == 2

    p = await controllers.user.delete_user(u_id)
    assert p.ok()
    p = await controllers.user.get_user(u_id)
    assert not p.ok()


@pytest.mark.asyncio
async def test_blob_curd(db_env):
    p = await controllers.user.create_user(res.UserData())
    assert p.ok()
    u_id = p.data().id

    p = await controllers.blob.insert_blob(
        u_id,
        res.BlobData(
            blob_type=BlobType.doc,
            blob_data={"content": "Hello world"},
            fields={"from": "happy"},
        ),
    )
    assert p.ok()
    b_id = p.data().id

    p = await controllers.blob.get_blob(u_id, b_id)
    assert p.ok()
    d = p.data()
    assert d.blob_type == BlobType.doc
    assert d.blob_data["content"] == "Hello world"
    assert d.fields["from"] == "happy"

    p = await controllers.blob.remove_blob(u_id, b_id)
    assert p.ok()
    p = await controllers.blob.get_blob(u_id, b_id)
    assert not p.ok()


@pytest.mark.asyncio
async def test_user_blob_curd(db_env):
    p = await controllers.user.create_user(res.UserData())
    assert p.ok()
    u_id = p.data().id

    p = await controllers.blob.insert_blob(
        u_id,
        res.BlobData(
            blob_type=BlobType.doc,
            blob_data={"content": "Hello world"},
            fields={"from": "happy"},
        ),
    )
    assert p.ok()
    b_id = p.data().id
    p = await controllers.blob.insert_blob(
        u_id,
        res.BlobData(
            blob_type=BlobType.doc,
            blob_data={"content": "Fool"},
            fields={"from": "happy"},
        ),
    )
    assert p.ok()
    b_id2 = p.data().id

    p = await controllers.user.get_user_all_blobs(u_id)
    assert p.ok()
    assert len(p.data().ids) == 2

    p = await controllers.user.delete_user(u_id)
    assert p.ok()

    p = await controllers.blob.get_blob(u_id, b_id)
    assert not p.ok()
    p = await controllers.blob.get_blob(u_id, b_id2)
    assert not p.ok()

    p = await controllers.user.get_user_all_blobs(u_id)
    assert len(p.data().ids) == 0
