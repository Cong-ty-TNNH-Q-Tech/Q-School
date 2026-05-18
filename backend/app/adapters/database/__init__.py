"""
Database Adapters — Concrete SQLAlchemy Repository implementations.
Member thêm export mới vào đây khi implement Repository.
"""
from app.adapters.database.base import BaseRepository
from app.adapters.database.user_repository import UserSQLAlchemyRepository

__all__ = [
    "BaseRepository",
    "UserSQLAlchemyRepository",
]
