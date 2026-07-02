"""
Pytest Shared Configuration and Fixtures.

Configures a clean test database lifecycle (SQLite aiosqlite), mounts
FastAPI testing clients with dependency overrides, and generates mock
Redis caching objects to ensure tests run completely isolated from external servers.
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.cache import CacheService, get_redis_client
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db
from main import app

from app.models.user import User

# Use a temporary SQLite database file for testing
TEST_DB_PATH = "./test_database.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="session")
def event_loop():
    """Create session-scoped event loop for async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def test_settings() -> Settings:
    """Override application settings for testing scope."""
    settings = get_settings()
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.ENVIRONMENT = "testing"
    settings.JWT_SECRET_KEY = "TEST-SECRET-KEY-MUST-BE-AT-LEAST-32-CHARS-FOR-SECURITY"
    settings.CACHE_ENABLED = True  # Enable mock caching logic in tests
    return settings



@pytest.fixture(scope="session")
async def test_engine(test_settings):
    """Create async SQLite engine for testing session."""
    # Ensure any previous test db is removed
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Teardown: close engine and drop database file
    await engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session per test, wrapped in a rollback transaction."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session_factory = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = session_factory()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """
    Mock the Redis cache service client completely.

    Prevents tests from attempting real connection to Redis.
    """
    mock_client = MagicMock()
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.get = AsyncMock(return_value=None)
    mock_client.set = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=True)
    mock_client.scan = AsyncMock(return_value=(0, []))

    # Mock the pipeline context manager
    mock_pipeline = AsyncMock()
    mock_pipeline.incr = AsyncMock()
    mock_pipeline.expire = AsyncMock()
    mock_pipeline.execute = AsyncMock(return_value=[1])

    # Async context manager __aenter__ returns the pipeline instance
    mock_client.pipeline = MagicMock(return_value=mock_pipeline)
    mock_pipeline.__aenter__ = AsyncMock(return_value=mock_pipeline)
    mock_pipeline.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr("app.core.cache.get_redis_client", lambda: mock_client)
    return mock_client



@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient with db dependency override."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    
    # Use ASGITransport in httpx
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session) -> User:
    """Create and return a default verified user profile in the database."""
    from app.core.security import PasswordHasher

    user = User(
        email="testuser@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=PasswordHasher.hash("SecureP@ss123!"),
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user) -> str:
    """Generate a valid JWT access token for the test user."""
    from app.core.security import JWTManager

    jwt_manager = JWTManager()
    return jwt_manager.create_access_token(str(test_user.id))


@pytest.fixture
def auth_headers(test_user_token) -> dict[str, str]:
    """Authorization header helper."""
    return {"Authorization": f"Bearer {test_user_token}"}
