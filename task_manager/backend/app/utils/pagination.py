"""
Pagination Helper Utilities.
"""

from typing import Any

from app.schemas.common import PaginatedMetadata


def get_pagination_metadata(total: int, page: int, page_size: int) -> PaginatedMetadata:
    """Calculate and return standardized pagination metadata."""
    total_pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedMetadata(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
