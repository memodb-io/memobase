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
)
from dataclasses import dataclass
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column,
    registry,
)
from sqlalchemy.sql import func
from .blob import BlobType

REG = registry()


@dataclass
class Base:
    __abstract__ = True

    # Common columns
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
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

    project_id: Mapped[str] = mapped_column(VARCHAR(63), nullable=False, unique=True)
    project_secret: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    profile_config: Mapped[str] = mapped_column(TEXT, nullable=True)

    __table_args__ = (Index("idx_projects_project_id", "project_id"),)


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


@REG.mapped_as_dataclass
class GeneralBlob(Base):
    __tablename__ = "general_blobs"

    # Specific columns
    blob_type: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    blob_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Relationships
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user: Mapped[User] = relationship(
        "User", back_populates="related_general_blobs", init=False
    )

    related_buffers: Mapped[list["BufferZone"]] = relationship(
        "BufferZone", back_populates="blob", cascade="all, delete-orphan", init=False
    )

    # Default columns
    additional_fields: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, default=None
    )
    __table_args__ = (
        Index("idx_general_blobs_user_id", "user_id"),
        Index("idx_general_blobs_user_id_id", "user_id", "id"),
        Index("idx_general_blobs_user_id_blob_type", "user_id", "blob_type"),
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
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user: Mapped[User] = relationship(
        "User", back_populates="related_buffers", init=False
    )

    blob_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("general_blobs.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    blob: Mapped[GeneralBlob] = relationship(
        "GeneralBlob", back_populates="related_buffers", init=False
    )

    __table_args__ = (
        Index("idx_buffer_zones_user_id_blob_type", "user_id", "blob_type"),
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
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        # Add index to this id
    )
    user: Mapped[User] = relationship(
        "User", back_populates="related_user_profiles", init=False
    )

    attributes: Mapped[dict] = mapped_column(JSONB, nullable=True, default=None)

    __table_args__ = (
        Index("idx_user_profiles_user_id", "user_id"),
        Index("idx_user_profiles_user_id_id", "user_id", "id"),
    )


@REG.mapped_as_dataclass
class UserEvent(Base):
    __tablename__ = "user_events"

    # Specific columns
    event_data: Mapped[dict] = mapped_column(JSONB)

    # Relationships
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        # Add index to this id
    )
    user: Mapped[User] = relationship(
        "User", back_populates="related_user_events", init=False
    )

    __table_args__ = (
        Index("idx_user_events_user_id", "user_id"),
        Index("idx_user_events_user_id_id", "user_id", "id"),
    )
