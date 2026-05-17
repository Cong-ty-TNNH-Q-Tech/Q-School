"""
Inbound Port — Auth Use Case Interface.
Router gọi interface này, không gọi thẳng vào Use Case class cụ thể.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.user import User


class IAuthUseCase(ABC):
    """Abstract Inbound Port: Contract cho Authentication Use Cases."""

    @abstractmethod
    async def register(
        self, username: str, email: str, password: str, role: str = "student"
    ) -> User:
        """
        Đăng ký tài khoản mới.
        Raise ConflictException nếu email/username đã tồn tại.
        """
        ...

    @abstractmethod
    async def login(self, email: str, password: str) -> dict:
        """
        Xác thực và trả về tokens.
        Return: {"user": User, "access_token": str, "refresh_token": str}
        Raise UnauthorizedException nếu sai credentials.
        """
        ...

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Đổi Refresh Token lấy Access Token mới.
        Return: {"access_token": str, "expires_in": int}
        Raise UnauthorizedException nếu refresh token hết hạn.
        """
        ...
