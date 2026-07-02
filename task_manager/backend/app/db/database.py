"""
Async Database Engine and Session Factory.

Manages the SQLAlchemy async engine lifecycle and provides
connection pooling configuration for production use.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level engine and session factory (initialized at startup)
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _create_engine() -> AsyncEngine:
    """
    Create an async SQLAlchemy engine with appropriate pooling.

    SQLite uses NullPool (no connection pooling) since it doesn't
    support concurrent connections well. PostgreSQL uses QueuePool
    with configurable pool size.
    """
    settings = get_settings()

    connect_args: dict = {}
    pool_class = QueuePool
    pool_kwargs: dict = {
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,
    }

    if settings.is_sqlite:
        connect_args = {"check_same_thread": False}
        pool_class = NullPool
        pool_kwargs = {}

    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        poolclass=pool_class,
        connect_args=connect_args,
        **pool_kwargs,
    )


def get_engine() -> AsyncEngine:
    """Get or create the async engine singleton."""
    global _engine  # noqa: PLW0603
    if _engine is None:
        _engine = _create_engine()
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the session factory singleton."""
    global _session_factory  # noqa: PLW0603
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def init_db() -> None:
    """
    Initialize the database engine at application startup.

    In development/testing with SQLite, creates tables directly.
    In production with PostgreSQL, Alembic handles migrations.
    """
    settings = get_settings()
    engine = get_engine()

    if settings.is_sqlite:
        from app.db.base import Base

        # Import all models so they register with Base.metadata
        import app.models.project  # noqa: F401
        import app.models.refresh_token  # noqa: F401
        import app.models.task  # noqa: F401
        import app.models.user  # noqa: F401

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    logger.info("database_initialized", database_url=settings.DATABASE_URL.split("@")[-1])


async def close_db() -> None:
    """Dispose of the database engine at application shutdown."""
    global _engine, _session_factory  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("database_closed")
