"""
Unit Tests for Utility Functions and Observability configurations.
"""

from app.utils.filters import clean_filters
from app.utils.pagination import get_pagination_metadata
from app.utils.search import format_ilike_query


def test_clean_filters():
    """Verify clean_filters removes None values from dict."""
    filters = {"title": "Task", "completed": None, "priority": "high"}
    cleaned = clean_filters(filters)
    assert cleaned == {"title": "Task", "priority": "high"}
    assert "completed" not in cleaned


def test_pagination_helper():
    """Verify pagination metadata calculations."""
    meta = get_pagination_metadata(total=45, page=3, page_size=10)
    assert meta.total == 45
    assert meta.page == 3
    assert meta.page_size == 10
    assert meta.total_pages == 5


def test_search_helper():
    """Verify formatting query for SQL ILIKE search pattern."""
    assert format_ilike_query("  my search  ") == "%my search%"
