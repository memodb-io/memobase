import pytest
import numpy as np
from unittest.mock import patch, AsyncMock, Mock
from memobase_server.env import CONFIG
from memobase_server.controllers import full as controllers
from memobase_server.models import response as res
from memobase_server.models.blob import BlobType
from memobase_server.models.database import DEFAULT_PROJECT_ID


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
async def test_user_state_clean(db_env):
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

    p = await controllers.profile.add_user_profiles(
        u_id, DEFAULT_PROJECT_ID, ["test"], [{"topic": "test", "sub_topic": "test"}]
    )
    assert p.ok()
    p = await controllers.profile.get_user_profiles(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
    d = p.data()
    assert len(d.profiles) == 1
    assert d.profiles[0].attributes == {"topic": "test", "sub_topic": "test"}

    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
    p = await controllers.user.get_user(u_id, DEFAULT_PROJECT_ID)
    assert not p.ok()
    p = await controllers.profile.get_user_profiles(u_id, DEFAULT_PROJECT_ID)
    assert p.ok() and len(p.data().profiles) == 0


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


@pytest.mark.asyncio
async def test_filter_user_events(db_env, mock_event_get_embedding):
    """Test the filter_user_events function with various filtering scenarios."""
    # Create a test user
    p = await controllers.user.create_user(res.UserData(), DEFAULT_PROJECT_ID)
    assert p.ok()
    u_id = p.data().id

    # Create test events with different tag configurations
    test_events = [
        # Event 1: emotion=happy, goal=relax
        {
            "profile_delta": [
                {
                    "content": "User is feeling good",
                    "attributes": {"topic": "mood", "sub_topic": "positive"},
                }
            ],
            "event_tip": "- User had a great day",
            "event_tags": [
                {"tag": "emotion", "value": "happy"},
                {"tag": "goal", "value": "relax"},
            ],
        },
        # Event 2: emotion=sad, location=home
        {
            "profile_delta": [
                {
                    "content": "User is feeling down",
                    "attributes": {"topic": "mood", "sub_topic": "negative"},
                }
            ],
            "event_tip": "- User had a rough day",
            "event_tags": [
                {"tag": "emotion", "value": "sad"},
                {"tag": "location", "value": "home"},
            ],
        },
        # Event 3: goal=work, location=office
        {
            "profile_delta": [
                {
                    "content": "User is focused on tasks",
                    "attributes": {"topic": "work", "sub_topic": "productivity"},
                }
            ],
            "event_tip": "- User is being productive",
            "event_tags": [
                {"tag": "goal", "value": "work"},
                {"tag": "location", "value": "office"},
            ],
        },
        # Event 4: emotion=happy, no other tags
        {
            "profile_delta": [
                {
                    "content": "User is excited",
                    "attributes": {"topic": "mood", "sub_topic": "positive"},
                }
            ],
            "event_tip": "- User is excited about something",
            "event_tags": [{"tag": "emotion", "value": "happy"}],
        },
        # Event 5: no event_tags at all
        {
            "profile_delta": [
                {
                    "content": "User shared information",
                    "attributes": {"topic": "info", "sub_topic": "general"},
                }
            ],
            "event_tip": "- User shared some general information",
        },
    ]

    # Insert all test events
    event_ids = []
    for event_data in test_events:
        p = await controllers.event.append_user_event(
            u_id, DEFAULT_PROJECT_ID, event_data
        )
        assert p.ok()
        event_ids.append(p.data())

    assert mock_event_get_embedding.await_count == len(test_events) * 2
    # Test 1: Filter by tag existence - events that have 'emotion' tag
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, has_event_tag=["emotion"]
    )
    assert p.ok()
    events = p.data().events
    events = [e.model_dump() for e in events]
    assert len(events) == 3  # Events 1, 2, and 4 have emotion tag
    emotion_values = [
        tag["value"]
        for event in events
        for tag in event["event_data"].get("event_tags", [])
        if tag["tag"] == "emotion"
    ]
    assert set(emotion_values) == {"happy", "sad"}

    # Test 2: Filter by exact tag-value - events where emotion=happy
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, event_tag_equal={"emotion": "happy"}
    )
    assert p.ok()
    events = p.data().events
    events = [e.model_dump() for e in events]
    assert len(events) == 2  # Events 1 and 4
    for event in events:
        emotion_tags = [
            tag
            for tag in event["event_data"].get("event_tags", [])
            if tag["tag"] == "emotion"
        ]
        assert len(emotion_tags) == 1
        assert emotion_tags[0]["value"] == "happy"

    # Test 3: Filter by multiple tag existence - events that have both 'emotion' and 'goal' tags
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, has_event_tag=["emotion", "goal"]
    )
    assert p.ok()
    events = p.data().events
    events = [e.model_dump() for e in events]
    assert len(events) == 1  # Only Event 1 has both emotion and goal tags
    event_tags = {tag["tag"] for tag in events[0]["event_data"]["event_tags"]}
    assert "emotion" in event_tags and "goal" in event_tags

    # Test 4: Filter by multiple exact tag-values
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, event_tag_equal={"emotion": "happy", "goal": "relax"}
    )
    assert p.ok()
    events = p.data().events
    events = [e.model_dump() for e in events]
    assert len(events) == 1  # Only Event 1 matches both conditions
    event_tags = {
        tag["tag"]: tag["value"] for tag in events[0]["event_data"]["event_tags"]
    }
    assert event_tags.get("emotion") == "happy"
    assert event_tags.get("goal") == "relax"

    # Test 5: Combine has_event_tag and event_tag_equal
    p = await controllers.event.filter_user_events(
        u_id,
        DEFAULT_PROJECT_ID,
        has_event_tag=["location"],
        event_tag_equal={"goal": "work"},
    )
    assert p.ok()
    events = p.data().events
    events = [e.model_dump() for e in events]
    assert len(events) == 1  # Only Event 3 has location tag AND goal=work
    event_tags = {
        tag["tag"]: tag["value"] for tag in events[0]["event_data"]["event_tags"]
    }
    assert "location" in event_tags
    assert event_tags.get("goal") == "work"

    # Test 6: Filter for non-existent tag
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, has_event_tag=["nonexistent"]
    )
    assert p.ok()
    events = p.data().events
    assert len(events) == 0  # No events should match

    # Test 7: Filter for non-existent tag value
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, event_tag_equal={"emotion": "angry"}
    )
    assert p.ok()
    events = p.data().events
    assert len(events) == 0  # No events have emotion=angry

    # Test 8: Test topk parameter
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, has_event_tag=["emotion"], topk=1
    )
    assert p.ok()
    events = p.data().events
    assert len(events) == 1  # Should return only 1 event due to topk limit

    # Test 9: No filters provided - should return all events
    p = await controllers.event.filter_user_events(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
    events = p.data().events
    assert len(events) == 5  # Should return all events

    # Test 10: Empty filter lists/dicts
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, has_event_tag=[], event_tag_equal={}
    )
    assert p.ok()
    events = p.data().events
    assert len(events) == 5  # Should return all events when filters are empty

    # Cleanup
    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()


@pytest.mark.asyncio
async def test_filter_user_events_edge_cases(db_env, mock_event_get_embedding):
    """Test edge cases for filter_user_events function."""
    # Create a test user
    p = await controllers.user.create_user(res.UserData(), DEFAULT_PROJECT_ID)
    assert p.ok()
    u_id = p.data().id

    # Test with user that has no events
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, has_event_tag=["emotion"]
    )
    assert p.ok()
    events = p.data().events
    assert len(events) == 0

    # Create an event with empty event_tags array
    event_data = {
        "profile_delta": [
            {
                "content": "Test content",
                "attributes": {"topic": "test", "sub_topic": "test"},
            }
        ],
        "event_tip": "- Test event",
        "event_tags": [],
    }
    p = await controllers.event.append_user_event(u_id, DEFAULT_PROJECT_ID, event_data)
    assert p.ok()

    # Filter should not match events with empty tags array
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, has_event_tag=["emotion"]
    )
    assert p.ok()
    events = p.data().events
    assert len(events) == 0

    # Create an event with null event_tags
    event_data_null_tags = {
        "profile_delta": [
            {
                "content": "Test content 2",
                "attributes": {"topic": "test", "sub_topic": "test"},
            }
        ],
        "event_tip": "- Test event 2",
        "event_tags": None,
    }
    p = await controllers.event.append_user_event(
        u_id, DEFAULT_PROJECT_ID, event_data_null_tags
    )
    assert p.ok()

    # Filter should still return 0 events
    p = await controllers.event.filter_user_events(
        u_id, DEFAULT_PROJECT_ID, has_event_tag=["emotion"]
    )
    assert p.ok()
    events = p.data().events
    assert len(events) == 0

    assert mock_event_get_embedding.await_count == 2 * 2

    # Cleanup
    p = await controllers.user.delete_user(u_id, DEFAULT_PROJECT_ID)
    assert p.ok()
