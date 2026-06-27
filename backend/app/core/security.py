"""
Security — JWT token handling và password hashing (bcrypt).
Tuân thủ quy tắc: Access Token 15 phút, Refresh Token 7 ngày.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

# ──────────────────────────────────────────────
# Password hashing (bcrypt via pwdlib)
# pwdlib là replacement hiện đại cho passlib (unmaintained), tương thích bcrypt v5+
_pwd_hasher = PasswordHash((BcryptHasher(),))

BCRYPT_MAX_BYTES = 72  # bcrypt hard limit


def hash_password(plain_password: str) -> str:
    """Mã hóa mật khẩu bằng bcrypt.

    bcrypt có giới hạn 72 bytes — nếu password dài hơn, truncate trước khi hash
    để đảm bảo hành vi nhất quán (bcrypt v5 raise ValueError thay vì silent truncate).
    """
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_BYTES:
        password_bytes = password_bytes[:BCRYPT_MAX_BYTES]
        plain_password = password_bytes.decode("utf-8", errors="ignore")
    return _pwd_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu plaintext khớp với hash hay không."""
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_BYTES:
        password_bytes = password_bytes[:BCRYPT_MAX_BYTES]
        plain_password = password_bytes.decode("utf-8", errors="ignore")
    return _pwd_hasher.verify(plain_password, hashed_password)


# ──────────────────────────────────────────────
# JWT
# ──────────────────────────────────────────────
class TokenPayload(TypedDict, total=False):
    """
    Cấu trúc JWT payload — dùng để type hint khi đọc payload từ decode_token().
    total=False để phần lớn field là optional (chỉ 'sub' và 'type' là bắt buộc).
    """

    sub: str  # user_id (UUID string)
    type: str  # 'access' | 'refresh'
    role: str  # 'student' | 'teacher' | 'admin' — chỉ có trong access token
    exp: int  # Thời gian hết hạn (Unix timestamp)
    iat: int  # Thời gian tạo (Unix timestamp)


def _create_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    """Tạo JWT token với thời gian hết hạn."""
    now = datetime.now(
        timezone.utc
    )  # Gọi 1 lần duy nhất — tránh iat/exp lệch microseconds
    to_encode = {**payload, "exp": now + expires_delta, "iat": now}
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


def decode_token(token: str) -> TokenPayload:
    """
    Giải mã và xác thực JWT token.
    Raise JWTError nếu token không hợp lệ hoặc đã hết hạn.

    Options rõ ràng:
    - verify_exp=True: Luôn kiểm tra exp claim (mặc định của jose nhưng explicit cho sự rõ ràng)
    - leeway=5: Cho phép ±5 giây clock skew giữa các server trong cluster/load balancer
    """
    return jwt.decode(  # type: ignore[return-value]
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_exp": True, "leeway": 5},
    )
