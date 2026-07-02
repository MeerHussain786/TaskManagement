"""
Filtering helper module.
"""

from typing import Any


def clean_filters(filters: dict[str, Any]) -> dict[str, Any]:
    """Strip out empty values from filters dictionary."""
    return {k: v for k, v in filters.items() if v is not None}
