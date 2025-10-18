"""
Database module for Prism application.
Handles SQLite database operations, schema creation, and data management.
"""

from .db_manager import DatabaseManager
from .schema import initialize_database

__all__ = ["DatabaseManager", "initialize_database"]
