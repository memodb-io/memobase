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
