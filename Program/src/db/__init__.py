"""
Database module for YouTube Study Notes AI.
Provides ORM models and database connection management.
"""

from .models import User, Note
from .database import create_db_and_tables, get_session

__all__ = [
    "User",
    "Note",
    "create_db_and_tables",
    "get_session",
]
