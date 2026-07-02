"""
Search text formatting helper module.
"""


def format_ilike_query(query: str) -> str:
    """Format query string into SQL ILIKE pattern."""
    return f"%{query.strip()}%"
