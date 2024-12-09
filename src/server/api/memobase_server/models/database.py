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
from sqlalchemy.ext.declarative import declarative_base
from .blob import BlobType

REG = registry()

Base = declarative_base()

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

    # In GeneralBlob class, add this relationship
    related_profiles: Mapped[list["UserProfile"]] = relationship(
        "UserProfile",
        secondary="user_profile_blobs",
        back_populates="related_blobs",
        init=False,
    )

    # Default columns
    additional_fields: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, default=None
    )
    __table_args__ = (Index("idx_general_blobs_user_id_id", "user_id", "id"),)

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
    # Relationships with blobs
    related_blobs: Mapped[list[GeneralBlob]] = relationship(
        "GeneralBlob",
        secondary="user_profile_blobs",
        back_populates="related_profiles",
        init=False,
    )

    attributes: Mapped[dict] = mapped_column(JSONB, nullable=True, default=None)


# Add this association table before the class definitions
user_profile_blobs = Table(
    "user_profile_blobs",
    REG.metadata,
    Column(
        "user_profile_id",
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    Column(
        "blob_id",
        UUID(as_uuid=True),
        ForeignKey("general_blobs.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)
