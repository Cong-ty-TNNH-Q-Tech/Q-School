"""
Base Pydantic Schemas — ApiResponse[T] và PaginatedResponse[T].

Mọi endpoint PHẢI trả về một trong hai schema này để đảm bảo
response format nhất quán theo chuẩn openapi.yaml:
  { "status": "success", "data": ..., "message": null, "error_code": 0 }

Ví dụ sử dụng trong Router:
    @router.get("/me", response_model=ApiResponse[UserOut])
    async def get_me(user: CurrentUserDep) -> ApiResponse[UserOut]:
        return ApiResponse(data=UserOut.model_validate(user))

    @router.get("/classes", response_model=PaginatedResponse[ClassOut])
    async def list_classes(...) -> PaginatedResponse[ClassOut]:
        return PaginatedResponse(
            data=[ClassOut.model_validate(c) for c in classes],
            next_cursor=records[-1].created_at.isoformat() if has_more else None,
            has_more=has_more,
        )
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standard single-item response wrapper.
    Dùng cho: POST (create), GET (single item), DELETE, PATCH.
    """

    status: str = "success"
    data: T
    message: str | None = None
    error_code: int = 0


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Cursor-based paginated response wrapper.
    Dùng cho: GET list endpoints.

    Composite Cursor (KHUYẾN NGHỊ):
      next_cursor_created_at: ISO datetime string của record cuối cùng.
      next_cursor_id: UUID string của record cuối cùng (tiebreaker).
      Dùng cả hai để tránh trùng/bỏ sót khi nhiều records có cùng created_at.

    has_more: True nếu còn dữ liệu phía sau cursor.

    KHÔNG dùng page/total_pages — cursor pagination theo chuẩn AGENTS.md.
    """

    status: str = "success"
    data: list[T]
    next_cursor_created_at: str | None = None  # ISO datetime của record cuối
    next_cursor_id: str | None = None  # UUID của record cuối (tiebreaker)
    has_more: bool = False
    error_code: int = 0
