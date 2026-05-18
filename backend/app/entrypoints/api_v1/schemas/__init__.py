"""
API v1 Schemas — Pydantic response/request models.
Import từ đây để dùng trong các routers.
"""
from app.entrypoints.api_v1.schemas.base import ApiResponse, PaginatedResponse
from app.entrypoints.api_v1.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    TokenData,
    ProfileOut,
    UserOut,
    LoginResponse,
)

__all__ = [
    # Base
    "ApiResponse",
    "PaginatedResponse",
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "RefreshRequest",
    "TokenData",
    "ProfileOut",
    "UserOut",
    "LoginResponse",
]
