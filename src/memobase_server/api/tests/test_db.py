import pytest
from sqlalchemy.inspection import inspect
from memobase_server.models.database import User, GeneralBlob
from memobase_server.connector import (
    Session,
    DB_ENGINE,
    db_health_check,
    redis_health_check,
)


def test_db_connection():
    assert db_health_check()
    assert redis_health_check()


def test_correct_tables():
    db_inspector = inspect(DB_ENGINE)
    assert "users" in db_inspector.get_table_names()
    assert "general_blobs" in db_inspector.get_table_names()


def test_user_model():
    with Session() as session:
        user = User(addional_fields={"name": "Gus"})
        session.add(user)
        session.commit()
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None

    with Session() as session:
        user = session.query(User).filter_by(id=user.id).first()
        assert user is not None
        assert user.addional_fields == {"name": "Gus"}

    # Test delete
    with Session() as session:
        user = session.query(User).filter_by(id=user.id).first()
        session.delete(user)
        session.commit()
        assert session.query(User).filter_by(id=user.id).first() is None


def test_general_blob_model():
    with Session() as session:
        user = User(addional_fields={"name": "blob_user"})
        session.add(user)
        session.commit()
        test_user_id = user.id
    with pytest.raises(AssertionError, match="Invalid blob type: fool_test"):
        GeneralBlob(blob_type="fool_test", blob_data=dict(), user_id=test_user_id)
