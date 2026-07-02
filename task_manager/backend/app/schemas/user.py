"""
User Pydantic Schemas.

Defines validation and serialization rules for registration,
profile updates, and user responses, enforcing complex password constraints.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Shared fields for User models."""

    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["john.doe@example.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username containing only alphanumeric characters and underscores",
        examples=["johndoe_99"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's full name",
        examples=["John Doe"],
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Enforce alphanumeric + underscore usernames."""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            msg = "Username must contain only letters, numbers, and underscores"
            raise ValueError(msg)
        return v


class UserCreate(UserBase):
    """Payload required to register a new user account."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description=(
            "Plaintext password. Must be at least 8 characters, "
            "and contain at least one uppercase letter, one lowercase letter, "
            "one number, and one special character."
        ),
        examples=["SecureP@ss123!"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password complexity rules."""
        if not any(c.isupper() for c in v):
            msg = "Password must contain at least one uppercase letter"
            raise ValueError(msg)
        if not any(c.islower() for c in v):
            msg = "Password must contain at least one lowercase letter"
            raise ValueError(msg)
        if not any(c.isdigit() for c in v):
            msg = "Password must contain at least one digit"
            raise ValueError(msg)
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            msg = "Password must contain at least one special character"
            raise ValueError(msg)
        return v


class UserUpdate(BaseModel):
    """Optional fields for updating a user profile."""

    email: EmailStr | None = Field(default=None, description="New email address")
    username: str | None = Field(default=None, min_length=3, max_length=50, description="New username")
    full_name: str | None = Field(default=None, min_length=1, max_length=255, description="New full name")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """Enforce alphanumeric + underscore usernames on update if provided."""
        if v is not None and not re.match(r"^[a-zA-Z0-9_]+$", v):
            msg = "Username must contain only letters, numbers, and underscores"
            raise ValueError(msg)
        return v


class UserResponse(UserBase):
    """Serialized user representation for API responses (excludes sensitive details)."""

    id: uuid.UUID = Field(..., description="Unique user identifier")
    is_active: bool = Field(..., description="Active status of the user profile")
    is_verified: bool = Field(..., description="Verification status of the email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Account last updated timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
