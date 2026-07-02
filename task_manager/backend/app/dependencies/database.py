"""
Database Dependency exports.

Wraps the database session builder to isolate dependency scopes.
"""

from app.db.session import get_db

__all__ = ["get_db"]
