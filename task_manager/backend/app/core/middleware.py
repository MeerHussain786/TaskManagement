"""
Middleware Stack.

Provides request/response processing middleware for:
- Correlation ID injection and propagation
- Request timing and performance logging
- Security headers (OWASP recommendations)
- Global exception handling with RFC 7807 responses
"""

import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppException
from app.core.logging import correlation_id_ctx, request_id_ctx

logger = structlog.get_logger(__name__)


# ── Correlation ID Middleware ────────────────────────────────────────────────


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Injects a correlation ID into every request.

    If the incoming request includes an X-Correlation-ID header, it is reused.
    Otherwise, a new UUID is generated. The correlation ID is propagated to:
    - Response headers
    - Structured log context
    - Downstream service calls
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with correlation ID."""
        cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        rid = str(uuid.uuid4())

        # Set context variables for structured logging
        correlation_id_ctx.set(cid)
        request_id_ctx.set(rid)

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        response.headers["X-Request-ID"] = rid

        return response


# ── Request Timing Middleware ────────────────────────────────────────────────


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Logs request duration and basic request metadata."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Time the request and log performance data."""
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"

        await logger.ainfo(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            client_ip=request.client.host if request.client else "unknown",
        )

        return response


# ── Security Headers Middleware ──────────────────────────────────────────────


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses.

    Implements OWASP security header recommendations to protect
    against common web vulnerabilities.
    """

    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


# ── Global Exception Handlers ───────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers on the FastAPI application.

    Produces RFC 7807 Problem Detail responses for all errors.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        await logger.awarning(
            "app_exception",
            error_code=exc.error_code,
            detail=exc.detail,
            status_code=exc.status_code,
            path=request.url.path,
        )
        content = {
            "type": f"about:blank#{exc.error_code}",
            "title": exc.error_code.replace("_", " ").title(),
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url.path),
        }
        if exc.extra:
            content["errors"] = exc.extra

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for unhandled exceptions. Prevents stack trace leakage."""
        await logger.aerror(
            "unhandled_exception",
            error_type=type(exc).__name__,
            detail=str(exc),
            path=request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "type": "about:blank#INTERNAL_ERROR",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred. Please try again later.",
                "instance": str(request.url.path),
            },
        )
