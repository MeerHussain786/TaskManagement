"""
Custom Exception Hierarchy.

Defines application-specific exceptions with HTTP status codes and
machine-readable error codes. All exceptions produce RFC 7807
Problem Detail responses via the global exception handler.
"""

from typing import Any


class AppException(Exception):
    """
    Base application exception.

    All custom exceptions inherit from this class to enable
    centralized exception handling in middleware.

    Attributes:
        status_code: HTTP status code for the response.
        error_code: Machine-readable error code string.
        detail: Human-readable error description.
        headers: Optional additional response headers.
    """

    def __init__(
        self,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        detail: str = "An unexpected error occurred",
        headers: dict[str, str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        self.headers = headers
        self.extra = extra or {}
        super().__init__(self.detail)


class AuthenticationException(AppException):
    """Raised when authentication fails (invalid credentials, expired token)."""

    def __init__(
        self,
        detail: str = "Could not validate credentials",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=401,
            error_code="AUTHENTICATION_FAILED",
            detail=detail,
            headers=headers or {"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(AppException):
    """Raised when user lacks permission for the requested operation."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(
            status_code=403,
            error_code="AUTHORIZATION_FAILED",
            detail=detail,
        )


class ValidationException(AppException):
    """Raised for business-rule validation failures."""

    def __init__(self, detail: str = "Validation failed", extra: dict[str, Any] | None = None) -> None:
        super().__init__(
            status_code=422,
            error_code="VALIDATION_ERROR",
            detail=detail,
            extra=extra,
        )


class NotFoundException(AppException):
    """Base not-found exception."""

    def __init__(self, resource: str = "Resource", resource_id: str = "") -> None:
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            status_code=404,
            error_code=f"{resource.upper()}_NOT_FOUND",
            detail=detail,
        )


class TaskNotFoundException(NotFoundException):
    """Raised when a requested task does not exist."""

    def __init__(self, task_id: str = "") -> None:
        super().__init__(resource="Task", resource_id=task_id)


class UserNotFoundException(NotFoundException):
    """Raised when a requested user does not exist."""

    def __init__(self, user_id: str = "") -> None:
        super().__init__(resource="User", resource_id=user_id)


class DatabaseException(AppException):
    """Raised for unrecoverable database errors."""

    def __init__(self, detail: str = "Database operation failed") -> None:
        super().__init__(
            status_code=503,
            error_code="DATABASE_ERROR",
            detail=detail,
        )


class RateLimitException(AppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded. Please try again later.") -> None:
        super().__init__(
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            detail=detail,
            headers={"Retry-After": "60"},
        )


class ConflictException(AppException):
    """Raised when a resource conflict occurs (e.g., duplicate email)."""

    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(
            status_code=409,
            error_code="CONFLICT",
            detail=detail,
        )
