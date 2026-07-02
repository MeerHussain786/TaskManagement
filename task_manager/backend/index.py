"""
Application Main Entry Point.

Sets up the FastAPI application context, registers middlewares, routers,
global exception handlers, CORS configs, and initializes database / redis
connections during lifecycle startup and shutdown events.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.cache import close_redis, get_redis_client
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.middleware import (
    CorrelationIdMiddleware,
    RequestTimingMiddleware,
    SecurityHeadersMiddleware,
    register_exception_handlers,
)
from app.db.database import close_db, init_db
from app.observability.metrics import setup_metrics
from app.observability.tracing import setup_tracing
from app.routers import auth_router, health_router, tasks_router, users_router

# Setup structured logger at module level
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown hooks.

    Initializes connection pools (SQLAlchemy Engine, Redis Client) on boot,
    and cleanly disposes of resources on termination.
    """
    settings = get_settings()
    logger.info("application_starting", version=settings.APP_VERSION, environment=settings.ENVIRONMENT.value)

    # Initialize Database connection pool
    await init_db()

    # Initialize Redis cache connection
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        logger.info("redis_connected", url=settings.REDIS_URL)
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))

    yield

    # Shutdown hooks
    logger.info("application_stopping")
    await close_db()
    await close_redis()
    logger.info("application_stopped")


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="Enterprise Task Management REST API built with Clean Architecture, FastAPI, and SQLAlchemy 2.0.",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── Middleware Stack ──────────────────────────────────────────────────
    # Note: Order is critical. Correlation ID runs first to attach log IDs
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ───────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ──────────────────────────────────────────────────────────
    api_prefix = settings.API_PREFIX
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(users_router, prefix=api_prefix)
    app.include_router(tasks_router, prefix=api_prefix)
    app.include_router(health_router, prefix=api_prefix)

    # ── Observability ────────────────────────────────────────────────────
    setup_metrics(app)
    setup_tracing(app)

    return app


app = create_app()
