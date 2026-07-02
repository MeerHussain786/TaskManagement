"""
Refresh Token Domain Model.

Stores hashed refresh tokens for JWT rotation and revocation.
Tokens are stored as SHA-256 hashes — never in plaintext.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base, UUIDMixin):
    """
    Refresh token model.

    Implements refresh token rotation: each use of a refresh token
    invalidates the old token and issues a new one. If a revoked
    token is used, all tokens for that user are invalidated (theft detection).

    Attributes:
        id: UUID primary key.
        user_id: FK to the owning user.
        token_hash: SHA-256 hash of the JWT refresh token.
        expires_at: Token expiration timestamp.
        revoked: Whether the token has been revoked.
        created_at: Token creation timestamp.
    """

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
        lazy="noload",
    )

    # ── Table Configuration ──────────────────────────────────────────────
    __table_args__ = (
        Index("ix_refresh_tokens_user_revoked", "user_id", "revoked"),
        {"comment": "JWT refresh tokens for token rotation"},
    )

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"
