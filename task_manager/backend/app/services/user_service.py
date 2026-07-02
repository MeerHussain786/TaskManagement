"""
User Profile Service.

Handles business queries for reading and updating authenticated user profiles,
ensuring uniqueness of updated credentials (email, username).
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UserNotFoundException
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate

logger = get_logger(__name__)


class UserService:
    """Business service governing User account operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_profile(self, user_id: uuid.UUID) -> User:
        """
        Fetch user profile details.

        Raises:
            UserNotFoundException: If the user ID does not exist.
        """
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        return user

    async def update_profile(self, user_id: uuid.UUID, payload: UserUpdate) -> User:
        """
        Update user profile attributes and enforce unique constraints.

        Raises:
            UserNotFoundException: If user ID does not exist.
            ConflictException: If new email or username is already taken.
        """
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))

        if payload.email and payload.email != user.email:
            if await self.user_repo.exists_by_email(payload.email):
                raise ConflictException("Email is already registered by another account")
            user.email = payload.email

        if payload.username and payload.username != user.username:
            if await self.user_repo.exists_by_username(payload.username):
                raise ConflictException("Username is already taken by another account")
            user.username = payload.username

        if payload.full_name:
            user.full_name = payload.full_name

        await self.user_repo.update(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info("user_profile_updated", user_id=user.id)
        return user
