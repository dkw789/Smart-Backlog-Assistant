"""Database layer for Smart Backlog Assistant.

This module provides database functionality:
- Database connection management
- Repository pattern implementation
- Model definitions and relationships
- Session management and transactions
"""

from .models import (
    Base,
    Job,
    User,
    Session,
)
from .repository import (
    DatabaseRepository,
    JobRepository,
    UserRepository,
)

__all__ = [
    "Base",
    "Job",
    "User", 
    "Session",
    "DatabaseRepository",
    "JobRepository",
    "UserRepository",
]
