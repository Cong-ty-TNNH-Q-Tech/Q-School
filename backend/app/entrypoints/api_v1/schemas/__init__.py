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
from app.entrypoints.api_v1.schemas.class_ import (
    CreateClassRequest,
    UpdateClassRequest,
    EnrollStudentRequest,
    ClassOut,
    ClassDetailOut,
    ClassStudentOut,
)
from app.entrypoints.api_v1.schemas.lesson import (
    CreateLessonRequest,
    UpdateLessonRequest,
    LessonOut,
)
from app.entrypoints.api_v1.schemas.rubric import (
    CreateRubricRequest,
    UpdateRubricRequest,
    RubricResponse,
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
    # Class
    "CreateClassRequest",
    "UpdateClassRequest",
    "EnrollStudentRequest",
    "ClassOut",
    "ClassDetailOut",
    "ClassStudentOut",
    # Lesson
    "CreateLessonRequest",
    "UpdateLessonRequest",
    "LessonOut",
    # Rubric
    "CreateRubricRequest",
    "UpdateRubricRequest",
    "RubricResponse",
]
