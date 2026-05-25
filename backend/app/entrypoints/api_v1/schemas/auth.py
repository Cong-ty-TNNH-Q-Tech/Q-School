"""
Auth Pydantic Schemas — Request/Response models cho Auth endpoints.
Định nghĩa theo openapi.yaml Group 1: AUTH & USERS.

NOTE: Dùng model_validate() (Pydantic v2) thay vì from_orm() (deprecated).
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


# ──────────────────────────────────────────────
# REQUEST SCHEMAS (Input Validation)
# ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    """POST /auth/login"""

    username: str  # username hoặc email
    password: str

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu không được để trống")
        return v

    @field_validator("username")
    @classmethod
    def normalize_username_or_email(cls, v: str) -> str:
        """
        Normalize input:
        - Trim whitespace ở đầu/cuối
        - Nếu trông giống email (chứa @) thì lowercase — khớp với DB lưu email lowercase
        - Nếu là username thì giữ nguyên case
        """
        v = v.strip()
        if not v:
            raise ValueError("Username/email không được để trống")
        if "@" in v:
            return v.lower()  # Normalize email
        return v


class RegisterRequest(BaseModel):
    """POST /auth/register"""

    username: str
    email: EmailStr
    password: str
    role: str = "student"

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError("username phải từ 3–50 ký tự")
        # Chỉ cho phép chữ cái, số, dấu gạch dưới, gạch ngang — an toàn cho URL, email, display name
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("username chỉ được chứa chữ cái, số, _, -")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Mật khẩu phải ít nhất 6 ký tự")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        allowed = {"student", "teacher"}
        if v not in allowed:
            raise ValueError(f"role phải là một trong: {allowed}")
        return v


class RefreshRequest(BaseModel):
    """POST /auth/refresh"""

    refresh_token: str


# ──────────────────────────────────────────────
# RESPONSE SCHEMAS (Output Serialization)
# ──────────────────────────────────────────────
class ProfileOut(BaseModel):
    """Thông tin Profile của User."""

    user_id: uuid.UUID
    full_name: str | None
    avatar_url: str | None
    school_name: str | None
    bio: str | None
    points: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    """
    Thông tin User public (không có password_hash).
    Dùng cho: /users/me, login response.
    """

    id: uuid.UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    profile: ProfileOut | None = None

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    """JWT token pair trả về sau login/refresh."""

    access_token: str
    refresh_token: str | None = None  # None khi chỉ refresh access token
    token_type: str = "bearer"
    expires_in: int  # giây


class LoginResponse(BaseModel):
    """Data field cho ApiResponse[LoginResponse]."""

    user: UserOut
    tokens: TokenData
