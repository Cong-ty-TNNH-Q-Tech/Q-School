"""
Auth Router — Driving Adapter (Primary).
Đây là PATTERN MẪU cho các Router khác.

Nguyên tắc Router trong Hexagonal Architecture:
  1. Nhận HTTP Request → validate bằng Pydantic Schema
  2. Inject dependencies (DbDep, CurrentUserDep) qua FastAPI Depends
  3. Khởi tạo Use Case với concrete Repository (DI thủ công, đơn giản hơn Container)
  4. Gọi Use Case → nhận kết quả
  5. Map kết quả → Response Schema → trả về HTTP Response
  6. Map Domain Exception → HTTP Exception (xử lý tại đây, KHÔNG trong Use Case)

Member: Copy pattern này khi tạo classes_router, quizzes_router...
"""
from fastapi import APIRouter, status

from app.adapters.database.user_repository import UserSQLAlchemyRepository
from app.application.use_cases.auth_use_case import AuthUseCase
from app.core.dependencies import DbDep, CurrentUserDep
from app.core.exceptions import (
    UnauthorizedException,
    ConflictException,
)
from app.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    InactiveUserError,
    UserNotFoundError,
)
from app.entrypoints.api_v1.schemas import (
    ApiResponse,
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    LoginResponse,
    TokenData,
    UserOut,
)

router = APIRouter()


# ──────────────────────────────────────────────
# Dependency Factory (Pattern cho team tham chiếu)
# Tạo Use Case với concrete adapter — không cần IoC Container
# ──────────────────────────────────────────────
def get_auth_use_case(db: DbDep) -> AuthUseCase:
    """
    Factory function để tạo AuthUseCase với concrete UserRepository.
    Dùng FastAPI Depends để inject vào endpoint.

    Member: Tạo tương tự get_class_use_case, get_quiz_use_case...
    """
    repo = UserSQLAlchemyRepository(db)
    return AuthUseCase(repo)


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────
@router.post(
    "/login",
    response_model=ApiResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập",
    description="Đăng nhập bằng username (hoặc email) + password. Trả về access_token (15 phút) và refresh_token (7 ngày).",
)
async def login(
    body: LoginRequest,
    db: DbDep,
) -> ApiResponse[LoginResponse]:
    """
    POST /auth/login
    Security: public (no auth required)
    """
    use_case = get_auth_use_case(db)
    try:
        result = await use_case.login(body.username, body.password)
    except InvalidCredentialsError as e:
        raise UnauthorizedException(str(e))
    except InactiveUserError as e:
        raise UnauthorizedException(str(e))

    return ApiResponse(
        data=LoginResponse(
            user=UserOut.model_validate(result["user"]),
            tokens=TokenData(
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                expires_in=result["expires_in"],
            ),
        ),
        message="Đăng nhập thành công",
    )


@router.post(
    "/register",
    response_model=ApiResponse[LoginResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Tạo tài khoản học sinh hoặc giáo viên mới. Trả về tokens ngay sau khi đăng ký.",
)
async def register(
    body: RegisterRequest,
    db: DbDep,
) -> ApiResponse[LoginResponse]:
    """
    POST /auth/register
    Security: public (no auth required)
    """
    use_case = get_auth_use_case(db)
    try:
        result = await use_case.register(
            username=body.username,
            email=str(body.email),
            password=body.password,
            role=body.role,
        )
    except UserAlreadyExistsError as e:
        raise ConflictException(str(e))

    return ApiResponse(
        data=LoginResponse(
            user=UserOut.model_validate(result["user"]),
            tokens=TokenData(
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                expires_in=result["expires_in"],
            ),
        ),
        message="Đăng ký thành công",
        error_code=0,
    )


@router.post(
    "/refresh",
    response_model=ApiResponse[TokenData],
    status_code=status.HTTP_200_OK,
    summary="Làm mới Access Token",
    description="Dùng refresh_token để lấy access_token mới. Tránh user phải login lại.",
)
async def refresh_token(
    body: RefreshRequest,
    db: DbDep,
) -> ApiResponse[TokenData]:
    """
    POST /auth/refresh
    Security: public (gửi kèm refresh_token trong body)
    """
    use_case = get_auth_use_case(db)
    try:
        result = await use_case.refresh_access_token(body.refresh_token)
    except (InvalidCredentialsError, UserNotFoundError, InactiveUserError) as e:
        raise UnauthorizedException(str(e))

    return ApiResponse(
        data=TokenData(
            access_token=result["access_token"],
            expires_in=result["expires_in"],
        ),
    )


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Đăng xuất",
    description="Client xóa token ở local. Server-side token revocation cần Redis blacklist (TODO).",
)
async def logout(
    _current_user: CurrentUserDep,
) -> ApiResponse[None]:
    """
    POST /auth/logout
    Security: Bearer token required

    TODO: Implement token blacklist bằng Redis để revoke token ngay lập tức.
    Hiện tại: Client xóa token ở local (stateless JWT).
    """
    # TODO: Thêm token vào Redis blacklist với TTL = remaining expiry time
    return ApiResponse(data=None, message="Đăng xuất thành công")


@router.get(
    "/me",
    response_model=ApiResponse[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin cá nhân",
    description="Trả về thông tin đầy đủ của user đang đăng nhập, bao gồm Profile.",
)
async def get_me(
    current_user: CurrentUserDep,
) -> ApiResponse[UserOut]:
    """
    GET /auth/me
    Security: Bearer token required

    NOTE: current_user đã được inject với Profile eager loaded bởi get_current_user dependency.
    Không cần gọi qua Use Case — tránh double DB query.
    """
    return ApiResponse(data=UserOut.model_validate(current_user))
