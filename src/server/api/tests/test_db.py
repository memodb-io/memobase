import pytest
from sqlalchemy.inspection import inspect
from memobase_server.models.database import User, GeneralBlob, UserProfile
from memobase_server.models.blob import BlobType
from memobase_server.connectors import (
    Session,
    DB_ENGINE,
)


def test_correct_tables(db_env):
    db_inspector = inspect(DB_ENGINE)
    assert "users" in db_inspector.get_table_names()
    assert "general_blobs" in db_inspector.get_table_names()


def test_user_model(db_env):
    with Session() as session:
        user = User(additional_fields={"name": "Gus"})
        session.add(user)
        session.commit()
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None

    with Session() as session:
        user = session.query(User).filter_by(id=user.id).first()
        assert user is not None
        assert user.additional_fields == {"name": "Gus"}

    # Test delete
    with Session() as session:
        user = session.query(User).filter_by(id=user.id).first()
        session.delete(user)
        session.commit()
        assert session.query(User).filter_by(id=user.id).first() is None


def test_general_blob_model(db_env):
    with Session() as session:
        user = User(additional_fields={"name": "blob_user"})
        session.add(user)
        session.commit()
        test_user_id = user.id
    with pytest.raises(AssertionError, match="Invalid blob type: fool_test"):
        GeneralBlob(blob_type="fool_test", blob_data=dict(), user_id=test_user_id)

    with Session() as session:
        user = session.query(User).filter_by(id=test_user_id).first()
        session.delete(user)
        session.commit()


def test_user_profile_model(db_env):
    with Session() as session:
        user = User(additional_fields={"name": "profile_user"})
        session.add(user)
        session.commit()
        test_user_id = user.id

    # create fake blob
    with Session() as session:
        blob = GeneralBlob(
            blob_type=BlobType.doc,
            blob_data={"content": "Hello, world!"},
            user_id=test_user_id,
        )
        test_blob_id = blob.id
        session.add(blob)
        session.commit()

    with Session() as session:
        profile = UserProfile(content="Hello, world!", user_id=test_user_id)
        profile2 = UserProfile(content="Hello, world!", user_id=test_user_id)
        blob = session.query(GeneralBlob).filter_by(id=test_blob_id).first()
        profile.related_blobs = [blob]
        profile2.related_blobs = [blob]
        session.add(profile)
        session.add(profile2)
        test_profile_id = profile.id
        session.commit()

    with Session() as session:
        profile = session.query(UserProfile).filter_by(id=test_profile_id).first()
        blob = session.query(GeneralBlob).filter_by(id=test_blob_id).first()
        assert len(profile.related_blobs) == 1
        assert len(blob.related_profiles) == 2
        print(profile.related_blobs[0].blob_data)

    # check related blobs and remove the last one
    with Session() as session:
        b = session.query(GeneralBlob).filter_by(id=test_blob_id).first()
        assert len(b.related_profiles) == 2
        session.delete(b)
        session.commit()

    with Session() as session:
        profile = session.query(UserProfile).filter_by(id=test_profile_id).first()
        assert len(profile.related_blobs) == 0

    with Session() as session:
        user = session.query(User).filter_by(id=test_user_id).first()
        session.delete(user)

        session.commit()
