"""
Generic Async Repository base implementation.

Encapsulates common database queries using SQLAlchemy 2.0 select / update / delete.
Allows subclasses to extend and write specialized queries.
"""

import uuid
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic Repository pattern implementation for CRUD operations.

    Args:
        model: The SQLAlchemy model class.
    """

    def __init__(self, model: type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get(self, id_: uuid.UUID) -> ModelType | None:
        """Fetch a single record by its UUID primary key."""
        query = select(self.model).where(self.model.id == id_)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[ModelType]:
        """Fetch all records of this model type."""
        query = select(self.model)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        """Add a new record to the session. Requires flush or commit to persist."""
        self.db.add(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Refresh reference and mark object as modified in the session."""
        self.db.add(obj)
        return obj

    async def delete(self, id_: uuid.UUID) -> bool:
        """Delete a record by its UUID primary key."""
        query = delete(self.model).where(self.model.id == id_)
        result = await self.db.execute(query)
        return (result.rowcount or 0) > 0
