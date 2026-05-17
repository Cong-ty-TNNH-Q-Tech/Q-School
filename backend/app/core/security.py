"""
Security — JWT token handling và password hashing (bcrypt).
Tuân thủ quy tắc: Access Token 15 phút, Refresh Token 7 ngày.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ──────────────────────────────────────────────
# Password hashing (bcrypt)
# ──────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Mã hóa mật khẩu bằng bcrypt."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu plaintext khớp với hash hay không."""
    return _pwd_context.verify(plain_password, hashed_password)


# ──────────────────────────────────────────────
# JWT
# ──────────────────────────────────────────────
def _create_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    """Tạo JWT token với thời gian hết hạn."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {**payload, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    """Tạo JWT Access Token (15 phút)."""
    return _create_token(
        payload={"sub": str(user_id), "role": role, "type": "access"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    """Tạo JWT Refresh Token (7 ngày)."""
    return _create_token(
        payload={"sub": str(user_id), "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Giải mã và xác thực JWT token.
    Raise JWTError nếu token không hợp lệ hoặc đã hết hạn.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
