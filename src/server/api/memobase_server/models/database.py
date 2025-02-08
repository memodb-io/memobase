import os
import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    VARCHAR,
    Integer,
    ForeignKey,
    TIMESTAMP,
    Table,
    TEXT,
    Column,
    Index,
    Boolean,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
)
from dataclasses import dataclass
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column,
    registry,
    object_session,
)
from sqlalchemy.sql import func
from sqlalchemy import event
from .blob import BlobType
from sqlalchemy.orm.attributes import get_history

REG = registry()
DEFAULT_PROJECT_ID = "__root__"
DEFAULT_PROJECT_SECRET = "__root__"


@dataclass
class Base:
    __abstract__ = True

    # Common columns
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        default_factory=uuid.uuid4,
        init=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), init=False
    )


@REG.mapped_as_dataclass
class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, unique=True)
    project_secret: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    profile_config: Mapped[str] = mapped_column(TEXT, nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="active")

    related_users: Mapped[list["User"]] = relationship(
        "User", back_populates="project", cascade="all, delete-orphan", init=False
    )

    __table_args__ = (
        PrimaryKeyConstraint("project_id"),
        Index("idx_projects_project_id", "project_id"),
    )

    @classmethod
    def initialize_root_project(cls, session):
        """Initialize the root project if it doesn't exist."""
        root_project = (
            session.query(cls).filter_by(project_id=DEFAULT_PROJECT_ID).first()
        )
        if not root_project:
            root_project = cls(
                project_id=DEFAULT_PROJECT_ID,
                project_secret=DEFAULT_PROJECT_SECRET,
                profile_config=None,
            )
            session.add(root_project)
            session.commit()
        return root_project


# TODO: add index for user id and ...
@REG.mapped_as_dataclass
class User(Base):
    __tablename__ = "users"
    # Relationships
    related_general_blobs: Mapped[list["GeneralBlob"]] = relationship(
        "GeneralBlob", back_populates="user", cascade="all, delete-orphan", init=False
    )
    related_buffers: Mapped[list["BufferZone"]] = relationship(
        "BufferZone", back_populates="user", cascade="all, delete-orphan", init=False
    )
    related_user_profiles: Mapped[list["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", cascade="all, delete-orphan", init=False
    )
    related_user_events: Mapped[list["UserEvent"]] = relationship(
        "UserEvent", back_populates="user", cascade="all, delete-orphan", init=False
    )

    # Default columns
    additional_fields: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, default=None
    )

    project_id: Mapped[Optional[str]] = mapped_column(
        VARCHAR(64),
        ForeignKey("projects.project_id", ondelete="CASCADE", onupdate="CASCADE"),
        init=True,
        default=DEFAULT_PROJECT_ID,
    )
    project: Mapped[Optional[Project]] = relationship(
        "Project", back_populates="related_users", init=False, foreign_keys=[project_id]
    )

    __table_args__ = (
        PrimaryKeyConstraint("id", "project_id"),
        Index("idx_users_id_project_id", "id", "project_id"),
    )


@REG.mapped_as_dataclass
class GeneralBlob(Base):
    __tablename__ = "general_blobs"

    # Add project_id to match Users table's composite key
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Specific columns
    blob_type: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    blob_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    related_buffers: Mapped[list["BufferZone"]] = relationship(
        "BufferZone",
        back_populates="blob",
        cascade="all, delete-orphan",
        init=False,
        overlaps="user,related_buffers",
    )

    # Default columns
    project_id: Mapped[str] = mapped_column(
        VARCHAR(64),
        default=DEFAULT_PROJECT_ID,
    )
    additional_fields: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, default=None
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="related_general_blobs",
        init=False,
        foreign_keys=[user_id, project_id],
    )
    __table_args__ = (
        PrimaryKeyConstraint("id", "project_id"),
        Index("idx_general_blobs_user_id_project_id", "user_id", "project_id"),
        Index("idx_general_blobs_user_id_id", "user_id", "project_id", "id"),
        Index(
            "idx_general_blobs_user_id_blob_type", "user_id", "project_id", "blob_type"
        ),
        Index("idx_general_blobs_id_project_id", "id", "project_id", unique=True),
        ForeignKeyConstraint(
            ["user_id", "project_id"],
            ["users.id", "users.project_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    # validate
    def __post_init__(self):
        assert isinstance(
            self.blob_type, BlobType
        ), f"Invalid blob type: {self.blob_type}"
        self.blob_type = self.blob_type.value


@REG.mapped_as_dataclass
class BufferZone(Base):
    __tablename__ = "buffer_zones"

    # Specific columns
    blob_type: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    token_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    blob_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    project_id: Mapped[str] = mapped_column(
        VARCHAR(64),
        default=DEFAULT_PROJECT_ID,
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="related_buffers",
        init=False,
        foreign_keys=[user_id, project_id],
        overlaps="blob,related_buffers",
    )

    blob: Mapped[GeneralBlob] = relationship(
        "GeneralBlob",
        back_populates="related_buffers",
        init=False,
        foreign_keys=[blob_id, project_id],
        overlaps="user,related_buffers",
    )
    __table_args__ = (
        PrimaryKeyConstraint("id", "project_id"),
        Index(
            "idx_buffer_zones_user_id_blob_type", "user_id", "project_id", "blob_type"
        ),
        ForeignKeyConstraint(
            ["user_id", "project_id"],
            ["users.id", "users.project_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["blob_id", "project_id"],
            ["general_blobs.id", "general_blobs.project_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    # validate
    def __post_init__(self):
        assert isinstance(
            self.blob_type, BlobType
        ), f"Invalid blob type: {self.blob_type}"
        self.blob_type = self.blob_type.value


@REG.mapped_as_dataclass
class UserProfile(Base):
    __tablename__ = "user_profiles"

    # Specific columns
    content: Mapped[str] = mapped_column(TEXT, nullable=False)

    # Relationships
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    attributes: Mapped[dict] = mapped_column(JSONB, nullable=True, default=None)

    project_id: Mapped[str] = mapped_column(
        VARCHAR(64),
        default=DEFAULT_PROJECT_ID,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="related_user_profiles",
        init=False,
        foreign_keys=[user_id, project_id],
    )

    __table_args__ = (
        PrimaryKeyConstraint("id", "project_id"),
        Index("idx_user_profiles_user_id_project_id", "user_id", "project_id"),
        Index("idx_user_profiles_user_id_id_project_id", "user_id", "project_id", "id"),
        ForeignKeyConstraint(
            ["user_id", "project_id"],
            ["users.id", "users.project_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )


@REG.mapped_as_dataclass
class UserEvent(Base):
    __tablename__ = "user_events"

    # Specific columns
    event_data: Mapped[dict] = mapped_column(JSONB)

    # Relationships

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    project_id: Mapped[str] = mapped_column(
        VARCHAR(64),
        default=DEFAULT_PROJECT_ID,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="related_user_events",
        init=False,
        foreign_keys=[user_id, project_id],
    )

    __table_args__ = (
        PrimaryKeyConstraint("id", "project_id"),
        Index("idx_user_events_user_id_project_id", "user_id", "project_id"),
        Index("idx_user_events_user_id_id_project_id", "user_id", "project_id", "id"),
        ForeignKeyConstraint(
            ["user_id", "project_id"],
            ["users.id", "users.project_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )


# Modify event listeners to allow root project initialization
@event.listens_for(Project, "before_insert")
def prevent_insert(mapper, connection, target):
    if target.project_id != DEFAULT_PROJECT_ID:
        raise ValueError("The projects table is read-only. Inserts are not allowed.")


@event.listens_for(Project, "before_delete")
def prevent_delete(mapper, connection, target):
    # if target.project_id != DEFAULT_PROJECT_ID:
    raise ValueError("The projects table is read-only. Deletions are not allowed.")


@event.listens_for(Project, "before_update")
def prevent_update(mapper, connection, target):
    session = object_session(target)
    if not session:
        return

    # Get the history of all attributes
    exclude_attrs = ["profile_config"]
    all_attrs = Project.__mapper__.attrs.keys()
    for attr in all_attrs:
        if attr in exclude_attrs:
            continue
        history = get_history(target, attr)
        if history.has_changes():
            raise ValueError(
                f"The projects table is read-only except for {exclude_attrs}. Updates to other fields are not allowed."
            )
