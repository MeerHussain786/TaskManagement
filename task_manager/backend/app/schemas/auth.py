"""
Authentication Pydantic Schemas.

Defines schemas for login, refresh token, and token response objects
with OpenAPI examples.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials required for login."""

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        description="User's plaintext password",
        examples=["P@ssw0rd123!"],
    )


class RefreshTokenRequest(BaseModel):
    """Request schema for obtaining a new access token via rotation."""

    refresh_token: str = Field(
        ...,
        description="Plaintext JWT refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


class TokenResponse(BaseModel):
    """Authentication token response payload."""

    access_token: str = Field(
        ...,
        description="Short-lived JWT access token for authorization",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        ...,
        description="Long-lived JWT refresh token for session maintenance",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="Bearer",
        description="Token authorization scheme (Bearer)",
        examples=["Bearer"],
    )
    expires_in: int = Field(
        ...,
        description="Access token lifetime in seconds",
        examples=[1800],
    )
