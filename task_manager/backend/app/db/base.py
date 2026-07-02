"""
SQLAlchemy Declarative Base and Mixins.

Provides the base class for all ORM models along with reusable
mixins for common patterns (timestamps, UUID primary keys).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base for all models.

    All ORM models must inherit from this class to be included
    in Alembic migrations and metadata operations.
    """

    pass


class UUIDMixin:
    """Mixin that adds a UUID primary key column."""

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamp columns.

    - created_at: Set once on record creation (server-side default).
    - updated_at: Updated automatically on every modification.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
