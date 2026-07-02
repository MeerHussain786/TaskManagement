"""
Database Session Dependency.

Provides async database sessions for FastAPI dependency injection.
Each request gets its own session with automatic cleanup.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    The session is automatically closed after the request completes,
    regardless of success or failure. Transactions are committed
    explicitly by the service layer.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
