"""
User Domain Model.

Represents application users with authentication credentials.
Supports email/username login with bcrypt-hashed passwords.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.refresh_token import RefreshToken
    from app.models.task import Task


class User(Base, UUIDMixin, TimestampMixin):
    """
    User account model.

    Attributes:
        id: UUID primary key.
        email: Unique email address (used for login).
        username: Unique display name.
        full_name: User's full name.
        hashed_password: bcrypt password hash.
        is_active: Account active flag (soft delete support).
        is_verified: Email verification status.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="1",
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────────────
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    # ── Table Configuration ──────────────────────────────────────────────
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        {"comment": "Application user accounts"},
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
