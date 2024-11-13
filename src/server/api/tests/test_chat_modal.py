import pytest
from unittest.mock import AsyncMock, Mock, patch
from memobase_server import controllers
from memobase_server.models import response as res
from memobase_server.models.blob import BlobType
from memobase_server.models.utils import Promise


GD_FACTS = {
    "facts": [
        {"memo": "MOCK user is called Gus", "cites": [0]},
        {
            "memo": "MOCK user really likes Chinese food",
            "cites": [1],
        },
        {
            "memo": "MOCK user is in high school and finds it boring",
            "cites": [1],
        },
    ]
}
PROFILES = [
    "user likes to play basketball",
    "user is a junior school student",
    "user likes chinese food",
    "user is 23 years old",
]
MERGE_FACTS = {
    "ADD": [{"new_index": 0}],
    "UPDATE": [
        {"old_index": 3, "new_index": 1, "memo": "User is 25 years old"},
        {
            "old_index": 1,
            "new_index": 2,
            "memo": "User is in high school and finds it boring",
        },
    ],
}


@pytest.fixture
def mock_llm_complete():
    with patch("memobase_server.controllers.modal.chat.llm_complete") as mock_llm:
        mock_client1 = AsyncMock()
        mock_client1.ok = Mock(return_value=True)
        mock_client1.data = Mock(return_value=GD_FACTS)

        mock_client2 = AsyncMock()
        mock_client2.ok = Mock(return_value=True)
        mock_client2.data = Mock(return_value=MERGE_FACTS)

        mock_llm.side_effect = [mock_client1, mock_client2]
        yield mock_llm


@pytest.mark.asyncio
async def test_chat_buffer_modal(db_env, mock_llm_complete):
    p = await controllers.user.create_user(res.UserData())
    assert p.ok()
    u_id = p.data().id

    p = await controllers.blob.insert_blob(
        u_id,
        res.BlobData(
            blob_type=BlobType.chat,
            blob_data={
                "messages": [
                    {"role": "user", "content": "Hello, this is Gus, how are you?"},
                    {"role": "assistant", "content": "I am fine, thank you!"},
                ]
            },
        ),
    )
    assert p.ok()
    b_id = p.data().id
    p = await controllers.blob.insert_blob(
        u_id,
        res.BlobData(
            blob_type=BlobType.chat,
            blob_data={
                "messages": [
                    {"role": "user", "content": "I really dig into Chinese food"},
                    {"role": "assistant", "content": "Got it, Gus!"},
                    {
                        "role": "user",
                        "content": "write me a homework letter about my final exam, high school is really boring.",
                    },
                ]
            },
            fields={"from": "happy"},
        ),
    )
    assert p.ok()
    b_id2 = p.data().id

    p = await controllers.buffer.get_buffer_capacity(u_id, BlobType.chat)
    assert p.ok() and p.data() == 2

    await controllers.buffer.flush_buffer(u_id, BlobType.chat)
    mock_llm_complete.assert_awaited_once()

    p = await controllers.user.get_user_profiles(u_id)
    assert p.ok()

    p = await controllers.buffer.get_buffer_capacity(u_id, BlobType.chat)
    assert p.ok() and p.data() == 0

    p = await controllers.user.delete_user(u_id)
    assert p.ok()


@pytest.mark.asyncio
async def test_chat_merge_modal(db_env, mock_llm_complete):
    p = await controllers.user.create_user(res.UserData())
    assert p.ok()
    u_id = p.data().id

    p = await controllers.blob.insert_blob(
        u_id,
        res.BlobData(
            blob_type=BlobType.chat,
            blob_data={
                "messages": [
                    {"role": "user", "content": "Hello, this is Gus, how are you?"},
                    {"role": "assistant", "content": "I am fine, thank you!"},
                    {"role": "user", "content": "I'm 25 now, how time flies!"},
                ]
            },
        ),
    )
    assert p.ok()
    b_id = p.data().id
    p = await controllers.blob.insert_blob(
        u_id,
        res.BlobData(
            blob_type=BlobType.chat,
            blob_data={
                "messages": [
                    {"role": "user", "content": "I really dig into Chinese food"},
                    {"role": "assistant", "content": "Got it, Gus!"},
                    {
                        "role": "user",
                        "content": "write me a homework letter about my final exam, high school is really boring.",
                    },
                ]
            },
            fields={"from": "happy"},
        ),
    )
    assert p.ok()
    b_id2 = p.data().id

    p = await controllers.user.add_user_profiles(
        u_id,
        PROFILES,
        [[] for _ in range(len(PROFILES))],
    )
    assert p.ok()
    await controllers.buffer.flush_buffer(u_id, BlobType.chat)
    assert mock_llm_complete.await_count == 2

    p = await controllers.user.get_user_profiles(u_id)
    assert p.ok() and len(p.data().profiles) == len(PROFILES) + 1

    p = await controllers.user.delete_user(u_id)
    assert p.ok()
