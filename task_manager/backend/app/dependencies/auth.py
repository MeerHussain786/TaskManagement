"""
Authentication Dependencies.

Validates the incoming OAuth2 JWT access token from the Authorization header,
fetches the associated user profile, and enforces account active checks.
"""

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AuthenticationException
from app.core.security import JWTManager
from app.dependencies.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# Configure FastAPI to inspect Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_settings().API_PREFIX}/auth/login"
)

_jwt_manager = JWTManager()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Validate access token and retrieve current user context.

    Raises:
        AuthenticationException: If token validation fails or user is missing.
    """
    try:
        payload = _jwt_manager.decode_token(token)
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise AuthenticationException(detail="Token contains no subject identity")
    except JWTError as e:
        raise AuthenticationException(detail="Failed to decode credentials token") from e

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as e:
        raise AuthenticationException(detail="Token subject must be a valid UUID") from e

    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)

    if not user:
        raise AuthenticationException(detail="User identity associated with token not found")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Enforce check that authenticated user's account is active.

    Raises:
        AuthenticationException: If user is inactive.
    """
    if not current_user.is_active:
        raise AuthenticationException(detail="User account is deactivated")
    return current_user
