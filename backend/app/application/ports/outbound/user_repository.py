"""
Outbound Port — Repository Interface cho User.
Use Cases phụ thuộc vào interface này, KHÔNG phụ thuộc vào SQLAlchemy cụ thể.
Adapter (adapters/database/user_repository.py) sẽ implement interface này.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.user import User


class IUserRepository(ABC):
    """Abstract Port: Định nghĩa contract cho User data access."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def create(self, username: str, email: str, password_hash: str, role: str) -> User: ...

    @abstractmethod
    async def update(self, user: User, **kwargs) -> User: ...

    @abstractmethod
    async def soft_delete(self, user: User) -> User: ...

    @abstractmethod
    async def is_email_taken(self, email: str) -> bool:
        """Kiểm tra email đã được đăng ký chưa (kể cả soft-deleted) — dùng khi đăng ký."""
        ...

    @abstractmethod
    async def is_username_taken(self, username: str) -> bool:
        """Kiểm tra username đã tồn tại chưa (kể cả soft-deleted) — dùng khi đăng ký."""
        ...
