import pytest
from unittest.mock import AsyncMock, Mock, patch
from memobase_server import controllers
from memobase_server.models import response as res
from memobase_server.models.database import DEFAULT_PROJECT_ID
from memobase_server.models.blob import BlobType
from memobase_server.models.utils import Promise
from memobase_server.env import CONFIG
import numpy as np


GD_FACTS = """
- basic_info::name::Gus
- interest::foods::Chinese food
- education::level::High School
- psychological::emotional_state::Feels bored with high school
"""

PROFILES = [
    "user likes to play basketball",
    "user is a junior school student",
    "user likes japanese food",
    "user is 23 years old",
]

PROFILE_ATTRS = [
    {"topic": "interest", "sub_topic": "sports"},
    {"topic": "education", "sub_topic": "level"},
    {"topic": "interest", "sub_topic": "foods"},
    {"topic": "basic_info", "sub_topic": "age"},
]

OVER_MAX_PROFILEs = ["Chinese food" for _ in range(20)]
OVER_MAX_PROFILE_ATTRS = [
    {"topic": "interest", "sub_topic": "foods" + str(i)} for i in range(20)
]

MERGE_FACTS = [
    """TTTT
---
1. UPDATE::Gus
2. UPDATE::user likes Chinese and Japanese food
3. UPDATE::High School
4. UPDATE::Feels bored with high school
"""
]

ORGANIZE_FACTS = """
- foods::Chinese food
"""


def dict_contains(a: dict, b: dict) -> bool:
    return all(a[k] == v for k, v in b.items())


@pytest.fixture
def mock_extract_llm_complete():
    with patch(
        "memobase_server.controllers.modal.chat.extract.llm_complete"
    ) as mock_llm:
        mock_client1 = AsyncMock()
        mock_client1.ok = Mock(return_value=True)
        mock_client1.data = Mock(return_value=GD_FACTS)

        mock_llm.side_effect = [mock_client1]
        yield mock_llm


@pytest.fixture
def mock_merge_llm_complete():
    with patch(
        "memobase_server.controllers.modal.chat.merge_yolo.llm_complete"
    ) as mock_llm:
        mock_client1 = AsyncMock()
        mock_client1.ok = Mock(return_value=True)
        mock_client1.data = Mock(return_value=MERGE_FACTS[0])

        mock_llm.side_effect = [mock_client1]
        yield mock_llm


@pytest.fixture
def mock_organize_llm_complete():
    with patch(
        "memobase_server.controllers.modal.chat.organize.llm_complete"
    ) as mock_llm:
        mock_client2 = AsyncMock()
        mock_client2.ok = Mock(return_value=True)
        mock_client2.data = Mock(return_value=ORGANIZE_FACTS)

        mock_llm.side_effect = [mock_client2]
        yield mock_llm


@pytest.fixture
def mock_event_tag_llm_complete():
    with patch(
        "memobase_server.controllers.modal.chat.event_summary.llm_complete"
    ) as mock_llm:

        mock_client2 = AsyncMock()
        mock_client2.ok = Mock(return_value=True)
        mock_client2.data = Mock(return_value="- emotion::happy")

        mock_llm.side_effect = [mock_client2]
        yield mock_llm


@pytest.fixture
def mock_entry_summary_llm_complete():
    with patch(
        "memobase_server.controllers.modal.chat.entry_summary.llm_complete"
    ) as mock_llm:

        mock_client2 = AsyncMock()
        mock_client2.ok = Mock(return_value=True)
        mock_client2.data = Mock(return_value="Melinda is a software engineer")

        mock_llm.side_effect = [mock_client2]
        yield mock_llm


@pytest.fixture
def mock_event_get_embedding():
    with patch(
        "memobase_server.controllers.event.get_embedding"
    ) as mock_event_get_embedding:
        async_mock = AsyncMock()
        async_mock.ok = Mock(return_value=True)
        async_mock.data = Mock(
            return_value=np.array([[0.1 for _ in range(CONFIG.embedding_dim)]])
        )
        mock_event_get_embedding.return_value = async_mock
        yield mock_event_get_embedding


@pytest.mark.asyncio
async def test_chat_buffer_modal(
    db_env,
    mock_extract_llm_complete,
    mock_merge_llm_complete,
    mock_event_tag_llm_complete,
    mock_entry_summary_llm_complete,
    mock_event_get_embedding,
):
    p = await controllers.user.create_user(res.UserData(), DEFAULT_PROJECT_ID)
    assert p.ok()
    u_id = p.data().id

    blob1 = res.BlobData(
        blob_type=BlobType.chat,
        blob_data={
            "messages": [
                {"role": "user", "content": "Hello, this is Gus, how are you?"},
                {"role": "assistant", "content": "I am fine, thank you!"},
            ]
        },
    )
    blob2 = res.BlobData(
        blob_type=BlobType.chat,
        blob_data={
            "messages": [
                {"role": "user", "content": "Hi, nice to meet you, I am Gus"},
                {
                    "role": "assistant",
                    "content": "Great! I'm Memobase Assistant, how can I help you?",
                },
                {"role": "user", "content": "I really dig into Chinese food"},
                {"role": "assistant", "content": "Got it, Gus!"},
                {
                    "role": "user",
                    "content": "write me a homework letter about my final exam, high school is really boring.",
                },
            ]
        },
        fields={"from": "happy"},
    )
    p = await controllers.blob.insert_blob(
        u_id,
        DEFAULT_PROJECT_ID,
        blob1,
    )
    assert p.ok()
    b_id = p.data().id
    await controllers.buffer.insert_blob_to_buffer(
        u_id, DEFAULT_PROJECT_ID, b_id, blob1.to_blob()
    )
    p = await controllers.blob.insert_blob(
        u_id,
        DEFAULT_PROJECT_ID,
        blob2,
    )
    assert p.ok()
    b_id2 = p.data().id
    await controllers.buffer.insert_blob_to_buffer(
        u_id, DEFAULT_PROJECT_ID, b_id2, blob2.to_blob()
    )

    p = await controllers.buffer.get_buffer_capacity(
        u_id, DEFAULT_PROJECT_ID, BlobType.chat
    )
    assert p.ok() and p.data() == 2

    await controllers.buffer.flush_buffer(u_id, DEFAULT_PROJECT_ID, BlobType.chat)

    p = await controllers.profile.get_user_profiles(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
    assert len(p.data().profiles) == 4
    print(p.data())

    p = await controllers.profile.truncate_profiles(p.data(), topk=2)
    assert p.ok()
    assert len(p.data().profiles) == 2

    p = await controllers.event.get_user_events(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
    assert len(p.data().events) == 1

    p = await controllers.buffer.get_buffer_capacity(
        u_id, DEFAULT_PROJECT_ID, BlobType.chat
    )
    assert p.ok() and p.data() == 0

    # persistent_chat_blobs default to True
    p = await controllers.user.get_user_all_blobs(
        u_id, DEFAULT_PROJECT_ID, BlobType.chat
    )
    assert p.ok() and len(p.data().ids) == 2

    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()

    mock_extract_llm_complete.assert_awaited_once()


@pytest.mark.asyncio
async def test_chat_merge_modal(
    db_env,
    mock_extract_llm_complete,
    mock_merge_llm_complete,
    mock_event_tag_llm_complete,
    mock_entry_summary_llm_complete,
    mock_event_get_embedding,
):
    p = await controllers.user.create_user(res.UserData(), DEFAULT_PROJECT_ID)
    assert p.ok()
    u_id = p.data().id

    blob1 = res.BlobData(
        blob_type=BlobType.chat,
        blob_data={
            "messages": [
                {"role": "user", "content": "Hello, this is Gus, how are you?"},
                {"role": "assistant", "content": "I am fine, thank you!"},
                {"role": "user", "content": "I'm 25 now, how time flies!"},
            ]
        },
    )
    blob2 = res.BlobData(
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
    )
    p = await controllers.blob.insert_blob(
        u_id,
        DEFAULT_PROJECT_ID,
        blob1,
    )
    assert p.ok()
    b_id = p.data().id
    await controllers.buffer.insert_blob_to_buffer(
        u_id, DEFAULT_PROJECT_ID, b_id, blob1.to_blob()
    )
    p = await controllers.blob.insert_blob(
        u_id,
        DEFAULT_PROJECT_ID,
        blob2,
    )
    assert p.ok()
    b_id2 = p.data().id
    await controllers.buffer.insert_blob_to_buffer(
        u_id, DEFAULT_PROJECT_ID, b_id2, blob2.to_blob()
    )

    p = await controllers.profile.add_user_profiles(
        u_id, DEFAULT_PROJECT_ID, PROFILES, PROFILE_ATTRS
    )
    assert p.ok()
    await controllers.buffer.flush_buffer(u_id, DEFAULT_PROJECT_ID, BlobType.chat)

    p = await controllers.profile.get_user_profiles(u_id, DEFAULT_PROJECT_ID)
    assert p.ok() and len(p.data().profiles) == len(PROFILES) + 2
    profiles = p.data().profiles
    profiles = sorted(profiles, key=lambda x: x.content)

    assert dict_contains(
        profiles[-1].attributes, {"topic": "interest", "sub_topic": "sports"}
    )
    assert profiles[-1].content == "user likes to play basketball"
    assert dict_contains(
        profiles[-2].attributes, {"topic": "interest", "sub_topic": "foods"}
    )
    assert profiles[-2].content == "user likes Chinese and Japanese food"

    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()

    assert mock_extract_llm_complete.await_count == 1
    assert mock_merge_llm_complete.await_count == 1


@pytest.mark.asyncio
async def test_chat_organize_modal(
    db_env,
    mock_extract_llm_complete,
    mock_merge_llm_complete,
    mock_organize_llm_complete,
    mock_event_tag_llm_complete,
    mock_entry_summary_llm_complete,
    mock_event_get_embedding,
):
    p = await controllers.user.create_user(res.UserData(), DEFAULT_PROJECT_ID)
    assert p.ok()
    u_id = p.data().id

    blob1 = res.BlobData(
        blob_type=BlobType.chat,
        blob_data={
            "messages": [
                {"role": "user", "content": "Hello, this is Gus, how are you?"},
                {"role": "assistant", "content": "I am fine, thank you!"},
                {"role": "user", "content": "I'm 25 now, how time flies!"},
            ]
        },
    )

    p = await controllers.blob.insert_blob(
        u_id,
        DEFAULT_PROJECT_ID,
        blob1,
    )
    assert p.ok()
    b_id = p.data().id
    await controllers.buffer.insert_blob_to_buffer(
        u_id, DEFAULT_PROJECT_ID, b_id, blob1.to_blob()
    )
    p = await controllers.profile.add_user_profiles(
        u_id, DEFAULT_PROJECT_ID, OVER_MAX_PROFILEs, OVER_MAX_PROFILE_ATTRS
    )
    assert p.ok()

    await controllers.buffer.flush_buffer(u_id, DEFAULT_PROJECT_ID, BlobType.chat)

    p = await controllers.profile.get_user_profiles(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()

    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
    assert mock_extract_llm_complete.await_count == 1
    assert mock_merge_llm_complete.await_count == 1
    assert mock_organize_llm_complete.await_count == 1
