"""
User Repository implementation.

Handles DB queries targeting the User model.
"""

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository managing User entity database transactions."""

    def __init__(self, db) -> None:
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Retrieve a user by their username."""
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        """Check if email is already registered."""
        user = await self.get_by_email(email)
        return user is not None

    async def exists_by_username(self, username: str) -> bool:
        """Check if username is already taken."""
        user = await self.get_by_username(username)
        return user is not None
