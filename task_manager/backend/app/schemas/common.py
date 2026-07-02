"""
Common Pydantic Schemas.

Contains reusable schemas for pagination, standard error responses,
and general metadata models.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedMetadata(BaseModel):
    """Metadata for paginated responses."""

    total: int = Field(description="Total number of items matching the query")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages available")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated list responses."""

    items: list[T] = Field(description="List of items for the current page")
    metadata: PaginatedMetadata = Field(description="Pagination metadata")


class ErrorResponseDetail(BaseModel):
    """Detailed validation error structure."""

    loc: list[str | int] = Field(description="Location of the validation error")
    msg: str = Field(description="Error message")
    type: str = Field(description="Type of error")


class ErrorResponse(BaseModel):
    """
    Standard RFC 7807 Problem Detail response.

    Used for structured error responses returned by the API.
    """

    type: str = Field(description="URI identifier for the error type")
    title: str = Field(description="Short, human-readable summary of the error type")
    status: int = Field(description="HTTP status code")
    detail: str = Field(description="Detailed explanation of this specific occurrence")
    instance: str = Field(description="URI reference for this request instance")
    errors: list[ErrorResponseDetail] | None = Field(default=None, description="Detailed field-level validation errors")


class HealthResponse(BaseModel):
    """System health check response."""

    status: str = Field(description="Overall system status (healthy/unhealthy)")
    version: str = Field(description="Application version")
    environment: str = Field(description="Current deployment environment")
    components: dict[str, str] = Field(description="Individual component health status (db, cache)")
