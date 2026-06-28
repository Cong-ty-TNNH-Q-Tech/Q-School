"""
Database Adapters — Concrete SQLAlchemy Repository implementations.
Member them export moi vao day khi implement Repository.
"""

from app.adapters.database.base import BaseRepository
from app.adapters.database.user_repository import UserSQLAlchemyRepository
from app.adapters.database.class_repository import ClassSQLAlchemyRepository
from app.adapters.database.lesson_repository import LessonSQLAlchemyRepository
from app.adapters.database.essay_repository import SQLAlchemyEssaySubmissionRepository

__all__ = [
    "BaseRepository",
    "UserSQLAlchemyRepository",
    "ClassSQLAlchemyRepository",
    "LessonSQLAlchemyRepository",
    "SQLAlchemyEssaySubmissionRepository",
]
