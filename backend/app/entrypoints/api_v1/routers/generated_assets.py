"""
Generated Assets Router — Issue #113.
POST /generated-assets   — tạo asset mới (AIUserDep: cần subscription active)
GET  /generated-assets   — danh sách assets của user (cursor pagination)
GET  /generated-assets/{id} — chi tiết một asset
"""

import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
import redis.asyncio as aioredis

from app.adapters.database.generated_asset_repository import (
    SQLAlchemyGeneratedAssetRepository,
)
from app.application.use_cases.generated_asset_use_case import (
    GeneratedAssetDTO,
    GeneratedAssetUseCase,
)
from app.core.dependencies import AIUserDep, CurrentUserDep, DbDep
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    TooManyRequestsException,
)
from app.domain.exceptions import AssetNotFoundError, AssetValidationError
from app.entrypoints.api_v1.schemas.base import ApiResponse, PaginatedResponse
from app.entrypoints.api_v1.schemas.generated_asset_schemas import (
    CreateAssetRequest,
    GeneratedAssetOut,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Rate Limiter Dependency ──────────────────────────────────────────────────


async def check_rate_limit(user: AIUserDep) -> None:
    """
    Rate Limiting Guard cho AI endpoints.
    Giới hạn: 5 requests / phút per user.
    Nếu vượt giới hạn, trả về HTTP 429 (Code: 4290).
    """
    from app.core.config import settings

    if not settings.REDIS_URL:
        return

    try:
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        key = f"rate_limit:{user.id}"
        
        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            await pipe.expire(key, 60, nx=True)
            result = await pipe.execute()
            
        count = result[0]
        await redis_client.aclose()
        
        if count > 5:
            raise TooManyRequestsException(
                "Rate limit exceeded. Please slow down. (Max 5 requests per minute)"
            )
    except TooManyRequestsException:
        raise
    except Exception as e:
        # Fail-open: log warning và bỏ qua nếu Redis gặp sự cố
        logger.warning(f"Rate limiter failed (fail-open): {e}")


# ── Dependency factory ────────────────────────────────────────────────────────


def get_use_case(db: DbDep) -> GeneratedAssetUseCase:
    """Tạo GeneratedAssetUseCase với SQLAlchemy adapter."""
    repo = SQLAlchemyGeneratedAssetRepository(db)
    
    from app.core.config import settings

    if not settings.VLLM_API_KEY or not settings.VLLM_API_URL:
        # Nếu không cấu hình API Key/URL (ví dụ ở local dev), trả về use case không có llm
        return GeneratedAssetUseCase(repo=repo, llm_client=None)

    from openai import AsyncOpenAI
    # Các cấu hình khác nếu lỗi sẽ được ném lên trên thay vì bị nuốt
    llm = AsyncOpenAI(
        api_key=settings.VLLM_API_KEY,
        base_url=settings.VLLM_API_URL,
    )

    return GeneratedAssetUseCase(repo=repo, llm_client=llm)


# ── Helper ────────────────────────────────────────────────────────────────────


def _dto_to_out(dto: GeneratedAssetDTO) -> GeneratedAssetOut:
    return GeneratedAssetOut(
        id=dto.id,
        creator_id=dto.creator_id,
        asset_type=dto.asset_type,
        input_params=dto.input_params,
        output_content=dto.output_content,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


# ── POST /generated-assets ────────────────────────────────────────────────────


@router.post(
    "",
    response_model=ApiResponse[GeneratedAssetOut],
    status_code=status.HTTP_202_ACCEPTED,
    summary="[AI] Tạo nội dung giáo dục mới (cần subscription)",
)
async def create_generated_asset(
    body: CreateAssetRequest,
    current_user: AIUserDep,
    use_case: GeneratedAssetUseCase = Depends(get_use_case),
) -> ApiResponse[GeneratedAssetOut]:
    """
    Sinh nội dung AI theo asset_type và input_params (Bất đồng bộ).
    Yêu cầu user có subscription active (402 nếu không có).
    Kiểm tra Rate Limiting (429 nếu vượt giới hạn).
    """
    # 1. Rate Limiting Check
    await check_rate_limit(current_user)

    # 2. Tạo blank asset
    try:
        dto = await use_case.pre_create_asset(
            creator_id=current_user.id,
            asset_type=body.asset_type,
            input_params=body.input_params,
        )
    except AssetValidationError as e:
        raise ValidationException(str(e))
    except AssetNotFoundError as e:
        raise NotFoundException(str(e))

    # 3. Đưa vào Celery Background Queue
    from app.entrypoints.celery_worker.ai_tasks import generate_asset_task
    generate_asset_task.delay(
        asset_id=str(dto.id),
        creator_id=str(current_user.id),
        asset_type=body.asset_type,
        input_params=body.input_params,
    )

    return ApiResponse(data=_dto_to_out(dto))


# ── GET /generated-assets ─────────────────────────────────────────────────────


@router.get(
    "",
    response_model=PaginatedResponse[GeneratedAssetOut],
    status_code=status.HTTP_200_OK,
    summary="[AI] Danh sách assets của user (cursor pagination)",
)
async def list_generated_assets(
    current_user: AIUserDep,
    use_case: GeneratedAssetUseCase = Depends(get_use_case),
    cursor_created_at: str | None = Query(
        default=None,
        description="ISO datetime của record cuối trang trước",
    ),
    cursor_id: uuid.UUID | None = Query(
        default=None,
        description="UUID của record cuối trang trước (tiebreaker)",
    ),
    limit: int = Query(default=20, ge=1, le=50, description="Số record mỗi trang"),
) -> PaginatedResponse[GeneratedAssetOut]:
    parsed_cursor_dt: datetime | None = None
    if cursor_created_at:
        try:
            parsed_cursor_dt = datetime.fromisoformat(cursor_created_at)
        except ValueError:
            parsed_cursor_dt = None

    try:
        result = await use_case.list_assets(
            creator_id=current_user.id,
            cursor_created_at=parsed_cursor_dt,
            cursor_id=cursor_id,
            limit=limit,
        )
    except AssetValidationError as e:
        raise ValidationException(str(e))
    except AssetNotFoundError as e:
        raise NotFoundException(str(e))

    return PaginatedResponse(
        data=[_dto_to_out(d) for d in result.items],
        next_cursor_created_at=result.next_cursor_created_at,
        next_cursor_id=result.next_cursor_id,
        has_more=result.has_more,
    )


# ── GET /generated-assets/{id} ────────────────────────────────────────────────


@router.get(
    "/{asset_id}",
    response_model=ApiResponse[GeneratedAssetOut],
    status_code=status.HTTP_200_OK,
    summary="Chi tiết một Generated Asset",
)
async def get_generated_asset(
    asset_id: uuid.UUID,
    current_user: CurrentUserDep,
    use_case: GeneratedAssetUseCase = Depends(get_use_case),
) -> ApiResponse[GeneratedAssetOut]:
    """Chỉ creator mới được xem asset của mình (trả 404 nếu không phải owner)."""
    try:
        dto = await use_case.get_asset(
            asset_id=asset_id,
            requester_id=current_user.id,
        )
    except AssetNotFoundError as e:
        raise NotFoundException(str(e))
    except AssetValidationError as e:
        raise ValidationException(str(e))
    return ApiResponse(data=_dto_to_out(dto))
