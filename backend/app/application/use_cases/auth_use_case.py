"""
AuthUseCase — Business logic cho Authentication.
Đây là PATTERN MẪU cho các Use Case khác.

Nguyên tắc Use Case trong Hexagonal Architecture:
  - Nhận INPUT từ Router (primitive types hoặc Pydantic models)
  - Gọi PORT (IUserRepository) để truy cập data — KHÔNG gọi SQLAlchemy trực tiếp
  - Raise DOMAIN EXCEPTIONS khi business rule vi phạm
  - Trả về DOMAIN OBJECTS hoặc DTOs

Member: Copy pattern này khi tạo ClassUseCase, QuizUseCase...
"""
import uuid

from app.application.ports.outbound.user_repository import IUserRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InactiveUserError,
)
from app.domain.models.user import User
from jose import JWTError


class AuthUseCase:
    """
    Use Case: Xử lý toàn bộ luồng Authentication.
    Inject IUserRepository qua constructor (Dependency Inversion).

    KHÔNG import FastAPI, KHÔNG import SQLAlchemy ở đây.
    """

    def __init__(self, user_repo: IUserRepository) -> None:
        self._repo = user_repo

    async def login(self, username: str, password: str) -> dict:
        """
        Đăng nhập bằng username hoặc email + password.
        Trả về access_token, refresh_token và thông tin user.

        Raises:
            InvalidCredentialsError: Sai username/email hoặc password.
            InactiveUserError: Tài khoản đã bị vô hiệu hóa.
        """
        # Thử lookup theo username trước, nếu không có thì lookup email
        user = await self._repo.get_by_username(username)
        if user is None:
            user = await self._repo.get_by_email(username)

        if user is None or not verify_password(password, user.password_hash):
            # Luôn raise cùng một loại lỗi để tránh user enumeration attack
            raise InvalidCredentialsError("Thông tin đăng nhập không đúng")

        if not user.is_active:
            raise InactiveUserError("Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên.")

        access_token = create_access_token(str(user.id), user.role)
        refresh_token = create_refresh_token(str(user.id))

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "student",
    ) -> dict:
        """
        Đăng ký tài khoản mới.
        Tạo User + Profile rỗng trong cùng transaction.

        Raises:
            UserAlreadyExistsError: Email hoặc username đã tồn tại.
        """
        # Kiểm tra unique constraints
        if await self._repo.is_email_taken(email):
            raise UserAlreadyExistsError("Email này đã được sử dụng")

        if await self._repo.is_username_taken(username):
            raise UserAlreadyExistsError("Username này đã được sử dụng")

        password_hash = hash_password(password)
        user = await self._repo.create(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
        )

        access_token = create_access_token(str(user.id), user.role)
        refresh_token = create_refresh_token(str(user.id))

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Cấp Access Token mới từ Refresh Token hợp lệ.
        Refresh Token không được renew — user phải login lại khi refresh hết hạn.

        Raises:
            InvalidCredentialsError: Token không hợp lệ, hết hạn, hoặc sai type.
            UserNotFoundError: User trong token không còn tồn tại.
            InactiveUserError: Tài khoản đã bị vô hiệu hóa.
        """
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise InvalidCredentialsError("Refresh token không hợp lệ hoặc đã hết hạn")

        if payload.get("type") != "refresh":
            raise InvalidCredentialsError("Token type không hợp lệ")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError("Token payload không hợp lệ")

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise InvalidCredentialsError("Token chứa user ID không hợp lệ")

        user = await self._repo.get_by_id(user_uuid)
        if user is None:
            raise UserNotFoundError("Tài khoản không còn tồn tại")

        if not user.is_active:
            raise InactiveUserError("Tài khoản đã bị vô hiệu hóa")

        new_access_token = create_access_token(str(user.id), user.role)

        return {
            "access_token": new_access_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def get_current_user_profile(self, user: User) -> User:
        """
        Trả về thông tin user hiện tại với Profile đầy đủ.
        User đã được inject bởi get_current_user dependency.
        """
        # Nếu profile chưa được load, fetch lại với eager loading
        if not hasattr(user, "profile") or user.profile is None:
            refreshed = await self._repo.get_by_id(user.id)
            if refreshed is None:
                raise UserNotFoundError("Không tìm thấy thông tin người dùng")
            return refreshed
        return user
