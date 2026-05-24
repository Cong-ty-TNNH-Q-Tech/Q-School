"""
Custom Exception Classes và FastAPI Exception Handlers.
Chuẩn response: {"status": "error", "message": "...", "error_code": XXXX}
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# ══════════════════════════════════════════════
# Base App Exception
# ══════════════════════════════════════════════
class AppException(Exception):
    """Base exception cho toàn bộ ứng dụng."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: int = 5000
    message: str = "Internal server error"

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


# ══════════════════════════════════════════════
# 4xx Client Errors
# ══════════════════════════════════════════════
class NotFoundException(AppException):
    """404 — Không tìm thấy resource."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = 4040
    message = "Resource not found"


class UnauthorizedException(AppException):
    """401 — Chưa xác thực / Token không hợp lệ."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 4010
    message = "Authentication required"


class ForbiddenException(AppException):
    """403 — Không có quyền truy cập."""

    status_code = status.HTTP_403_FORBIDDEN
    error_code = 4030
    message = "Access forbidden"


class ConflictException(AppException):
    """409 — Dữ liệu đã tồn tại (VD: email trùng)."""

    status_code = status.HTTP_409_CONFLICT
    error_code = 4090
    message = "Resource already exists"


class ValidationException(AppException):
    """422 — Dữ liệu đầu vào không hợp lệ."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = 4220
    message = "Validation error"


class PaymentRequiredException(AppException):
    """402 — Hết lượt AI / Gói cước hết hạn (SaaS Billing — Code: 4020)."""

    status_code = status.HTTP_402_PAYMENT_REQUIRED
    error_code = 4020
    message = "Subscription required or quota exceeded. Please upgrade your plan."


class TooManyRequestsException(AppException):
    """429 — Vượt quá Rate Limit (SaaS — Code: 4290)."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = 4290
    message = "Rate limit exceeded. Please slow down."


# ══════════════════════════════════════════════
# Exception Handlers (đăng ký vào FastAPI app)
# ══════════════════════════════════════════════
def _error_response(
    status_code: int, error_code: int, message: str, headers: dict | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        headers=headers,
        content={
            "status": "error",
            "data": None,
            "message": message,
            "error_code": error_code,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Đăng ký toàn bộ exception handlers vào FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        # RFC 7235: 401 PHẢI có WWW-Authenticate header
        headers = None
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            headers = {"WWW-Authenticate": "Bearer"}
        return _error_response(exc.status_code, exc.error_code, exc.message, headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in exc.errors()
        ]
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            4220,
            " | ".join(errors),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        from app.core.config import settings as _settings

        # DEBUG mode: expose exception detail để developer debug dễ
        # Production: che giấu internal error detail khỏi client
        message = str(exc) if _settings.DEBUG else "An unexpected error occurred."
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            5000,
            message,
        )
