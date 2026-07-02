"""
Structured Logging Configuration.

Uses structlog for JSON-formatted, machine-parseable log output.
Integrates correlation IDs and request context for distributed tracing.
"""

import logging
import sys
from contextvars import ContextVar

import structlog

from app.core.config import get_settings

# ── Context Variables ────────────────────────────────────────────────────────

correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


# ── Custom Processors ───────────────────────────────────────────────────────


def add_correlation_id(
    logger: logging.Logger,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: dict,
) -> dict:
    """Inject correlation ID from context into log events."""
    cid = correlation_id_ctx.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


def add_request_id(
    logger: logging.Logger,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: dict,
) -> dict:
    """Inject request ID from context into log events."""
    rid = request_id_ctx.get()
    if rid:
        event_dict["request_id"] = rid
    return event_dict


def add_app_info(
    logger: logging.Logger,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: dict,
) -> dict:
    """Add application metadata to all log events."""
    settings = get_settings()
    event_dict["service"] = settings.APP_NAME
    event_dict["version"] = settings.APP_VERSION
    
    env = settings.ENVIRONMENT
    event_dict["environment"] = env.value if hasattr(env, "value") else env
    return event_dict



# ── Setup ────────────────────────────────────────────────────────────────────


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    In production: JSON output with full context.
    In development: Pretty-printed console output for readability.
    """
    settings = get_settings()

    # pyrefly: ignore [bad-assignment]
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        add_request_id,
        add_app_info,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.LOG_FORMAT == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to route through structlog
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Suppress noisy third-party loggers
    for logger_name in ("uvicorn.access", "sqlalchemy.engine", "httpx"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
