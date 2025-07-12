import os
import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    text,
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
from ..env import (
    ProjectStatus,
    BillingStatus,
    BILLING_REFILL_AMOUNT_MAP,
    CONFIG,
    LOG,
    BufferStatus,
)
from sqlalchemy.orm.attributes import get_history
from pgvector.sqlalchemy import Vector

REG = registry()
DEFAULT_PROJECT_ID = "__root__"
DEFAULT_PROJECT_SECRET = "__root__"


def next_month_first_day() -> datetime:
    today = datetime.now()
    # If we're in the last month of the year, move to January of next year
    if today.month == 12:
        return datetime(today.year + 1, 1, 1)
    # Otherwise, move to the first day of next month
    return datetime(today.year, today.month + 1, 1)


def check_legal_embedding_dim(cls, session):
    try:
        # Use table_name from the ORM class to avoid hardcoding
        table_name = cls.__tablename__

        # Use text() to properly declare SQL expression
        sql = text(
            """
        SELECT atttypmod
        FROM pg_attribute
        JOIN pg_class ON pg_attribute.attrelid = pg_class.oid
        JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
        WHERE pg_class.relname = :table_name
        AND pg_attribute.attname = 'embedding'
        AND pg_namespace.nspname = current_schema();
        """
        )

        result = session.execute(sql, {"table_name": table_name}).scalar()

        # Table or column might not exist yet
        if result is None:
            raise ValueError(
                "`embedding` column does not exist in the table, please check the table schema"
            )

        # In pgvector, atttypmod - 8 is the dimension
        actual_dim = result

        if actual_dim != CONFIG.embedding_dim:
            raise ValueError(
                f"Configuration embedding dimension ({CONFIG.embedding_dim}) "
                f"does not match database dimension ({actual_dim}). "
                f"This may cause errors when inserting embeddings."
            )
        LOG.info(
            f"Configuration embedding dimension ({CONFIG.embedding_dim}) "
            f"matches database dimension ({actual_dim}). "
        )
        return actual_dim

    except Exception as e:
        LOG.warning(f"Failed to check embedding dimension: {str(e)}")
        raise e


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
        TIMESTAMP(timezone=True), server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        init=False,
    )


SHORT_ENUM_SIZE = 16


@REG.mapped_as_dataclass
class Billing(Base):
    __tablename__ = "billings"

    # Specific columns

    usage_left: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default_factory=lambda: BILLING_REFILL_AMOUNT_MAP[BillingStatus.free],
    )

    next_refill_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default_factory=next_month_first_day
    )
    # Relationships
    related_projects: Mapped[list["ProjectBilling"]] = relationship(
        "ProjectBilling",
        back_populates="billing",
        cascade="all, delete-orphan",
        init=False,
    )

    __table_args__ = (PrimaryKeyConstraint("id"),)


@REG.mapped_as_dataclass
class ProjectBilling:
    __tablename__ = "project_billings"

    project_id: Mapped[str] = mapped_column(
        VARCHAR(64),
        ForeignKey("projects.project_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    billing_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("billings.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), init=False
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", back_populates="billing_link", init=False
    )
    billing: Mapped[Billing] = relationship(
        "Billing", back_populates="related_projects", init=False
    )

    __table_args__ = (
        PrimaryKeyConstraint("project_id", "billing_id"),
        Index("idx_project_billings_project_id", "project_id"),
        Index("idx_project_billings_billing_id", "billing_id"),
    )


@REG.mapped_as_dataclass
class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, unique=True)
    project_secret: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    profile_config: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    status: Mapped[str] = mapped_column(
        VARCHAR(SHORT_ENUM_SIZE), nullable=False, default=ProjectStatus.active
    )

    related_users: Mapped[list["User"]] = relationship(
        "User", back_populates="project", cascade="all, delete-orphan", init=False
    )

    billing_link: Mapped[list[ProjectBilling]] = relationship(
        "ProjectBilling",
        back_populates="project",
        cascade="all, delete-orphan",
        init=False,
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
        if_project_billing = (
            session.query(ProjectBilling)
            .filter_by(project_id=DEFAULT_PROJECT_ID)
            .one_or_none()
        )
        if if_project_billing is None:
            billing = Billing(usage_left=BILLING_REFILL_AMOUNT_MAP[BillingStatus.free])
            session.add(billing)
            session.add(
                ProjectBilling(project_id=DEFAULT_PROJECT_ID, billing_id=billing.id)
            )
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
    related_user_event_gists: Mapped[list["UserEventGist"]] = relationship(
        "UserEventGist", back_populates="user", cascade="all, delete-orphan", init=False
    )
    related_user_statuses: Mapped[list["UserStatus"]] = relationship(
        "UserStatus", back_populates="user", cascade="all, delete-orphan", init=False
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
    blob_type: Mapped[str] = mapped_column(VARCHAR(SHORT_ENUM_SIZE), nullable=False)
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
    blob_type: Mapped[str] = mapped_column(VARCHAR(SHORT_ENUM_SIZE), nullable=False)
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

    status: Mapped[str] = mapped_column(
        VARCHAR(SHORT_ENUM_SIZE), nullable=False, default=BufferStatus.idle
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
            "idx_buffer_zones_user_id_blob_type",
            "user_id",
            "project_id",
            "blob_type",
            "status",
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

    embedding: Mapped[Vector] = mapped_column(
        Vector(dim=CONFIG.embedding_dim), nullable=True, default=None
    )

    related_user_event_gists: Mapped[list["UserEventGist"]] = relationship(
        "UserEventGist",
        back_populates="event",
        cascade="all, delete-orphan",
        init=False,
        overlaps="related_user_event_gists",
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

    @classmethod
    def check_legal_embedding_dim(cls, session):
        check_legal_embedding_dim(cls, session)
        LOG.info("UserEvent embedding dimension checked")


@REG.mapped_as_dataclass
class UserEventGist(Base):
    __tablename__ = "user_event_gists"

    # Specific columns
    gist_data: Mapped[dict] = mapped_column(JSONB)

    # Relationships
    event_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    project_id: Mapped[str] = mapped_column(
        VARCHAR(64),
        default=DEFAULT_PROJECT_ID,
    )

    event: Mapped[UserEvent] = relationship(
        "UserEvent",
        back_populates="related_user_event_gists",
        init=False,
        foreign_keys=[event_id, project_id],
        overlaps="related_user_event_gists",
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="related_user_event_gists",
        init=False,
        foreign_keys=[user_id, project_id],
        overlaps="event,related_user_event_gists",
    )

    embedding: Mapped[Vector] = mapped_column(
        Vector(dim=CONFIG.embedding_dim), nullable=True, default=None
    )

    __table_args__ = (
        PrimaryKeyConstraint("id", "project_id"),
        Index("idx_user_event_gists_user_id_project_id", "user_id", "project_id"),
        Index(
            "idx_user_event_gists_user_id_project_id_id", "user_id", "project_id", "id"
        ),
        Index(
            "idx_user_event_gists_user_id_id_project_id",
            "user_id",
            "project_id",
            "event_id",
        ),
        ForeignKeyConstraint(
            ["user_id", "project_id"],
            ["users.id", "users.project_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["event_id", "project_id"],
            ["user_events.id", "user_events.project_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    @classmethod
    def check_legal_embedding_dim(cls, session):
        check_legal_embedding_dim(cls, session)
        LOG.info("UserEventGist embedding dimension checked")


@REG.mapped_as_dataclass
class UserStatus(Base):
    __tablename__ = "user_statuses"

    # Specific columns
    type: Mapped[str] = mapped_column(VARCHAR(SHORT_ENUM_SIZE * 2), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False)

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
        back_populates="related_user_statuses",
        init=False,
        foreign_keys=[user_id, project_id],
    )

    __table_args__ = (
        PrimaryKeyConstraint("id", "project_id"),
        Index("idx_user_statuses_user_id_project_id", "user_id", "project_id"),
        Index(
            "idx_user_statuses_user_id_project_id_type", "user_id", "project_id", "type"
        ),
        Index("idx_user_statuses_user_id_id_project_id", "user_id", "project_id", "id"),
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
