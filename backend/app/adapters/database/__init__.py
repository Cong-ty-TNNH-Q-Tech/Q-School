"""
Database Adapters — Concrete SQLAlchemy Repository implementations.
Member thêm export mới vào đây khi implement Repository.
"""
from app.adapters.database.base import BaseRepository
from app.adapters.database.user_repository import UserSQLAlchemyRepository
from app.adapters.database.rubric_repository import RubricSQLAlchemyRepository

__all__ = [
    "BaseRepository",
    "UserSQLAlchemyRepository",
    "RubricSQLAlchemyRepository",
]
