"""
AI Prompts Router — CRUD endpoints cho Admin quản lý System Prompt/Persona.
Issue #114: Cho phép Admin tùy chỉnh AI persona qua Web UI mà không cần deploy lại.

Tất cả endpoints đều nằm dưới prefix /api/v1/ai-prompts (đăng ký trong __init__.py).
"""

import uuid

from fastapi import APIRouter, Depends, status

from app.application.use_cases.ai_prompt_use_case import AIPromptDTO, AIPromptUseCase
from app.adapters.database.ai_prompt_repository import SQLAlchemyAIPromptRepository
from app.core.dependencies import AdminDep, DbDep
from app.entrypoints.api_v1.schemas.base import ApiResponse
from app.entrypoints.api_v1.schemas.ai_prompt_schemas import (
    AIPromptResponse,
    CreateAIPromptRequest,
    UpdateAIPromptRequest,
)

router = APIRouter()


# ── Dependency ────────────────────────────────────────────────────────────────


def get_use_case(db: DbDep) -> AIPromptUseCase:
    """Factory: tạo AIPromptUseCase với SQLAlchemy adapter cho mỗi request."""
    repo = SQLAlchemyAIPromptRepository(db)
    return AIPromptUseCase(repo)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _to_response(dto: AIPromptDTO) -> AIPromptResponse:
    return AIPromptResponse(
        id=dto.id,
        persona_name=dto.persona_name,
        system_prompt_template=dto.system_prompt_template,
        version=dto.version,
        updated_at=dto.updated_at,
    )


# ── POST /ai-prompts ──────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=ApiResponse[AIPromptResponse],
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Tạo mới AI Prompt / Persona",
)
async def create_ai_prompt(
    body: CreateAIPromptRequest,
    _admin: AdminDep,
    use_case: AIPromptUseCase = Depends(get_use_case),
) -> ApiResponse[AIPromptResponse]:
    dto = await use_case.create(
        persona_name=body.persona_name,
        system_prompt_template=body.system_prompt_template,
        version=body.version,
    )
    return ApiResponse(data=_to_response(dto))


# ── GET /ai-prompts ───────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=ApiResponse[list[AIPromptResponse]],
    status_code=status.HTTP_200_OK,
    summary="[Admin] Lấy danh sách tất cả AI Prompts",
)
async def list_ai_prompts(
    _admin: AdminDep,
    use_case: AIPromptUseCase = Depends(get_use_case),
) -> ApiResponse[list[AIPromptResponse]]:
    dtos = await use_case.list_all()
    return ApiResponse(data=[_to_response(d) for d in dtos])


# ── GET /ai-prompts/{id} ──────────────────────────────────────────────────────


@router.get(
    "/{prompt_id}",
    response_model=ApiResponse[AIPromptResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết AI Prompt theo ID",
)
async def get_ai_prompt(
    prompt_id: uuid.UUID,
    use_case: AIPromptUseCase = Depends(get_use_case),
) -> ApiResponse[AIPromptResponse]:
    dto = await use_case.get_by_id(prompt_id)
    return ApiResponse(data=_to_response(dto))


# ── PATCH /ai-prompts/{id} ────────────────────────────────────────────────────


@router.patch(
    "/{prompt_id}",
    response_model=ApiResponse[AIPromptResponse],
    status_code=status.HTTP_200_OK,
    summary="[Admin] Cập nhật system_prompt_template / version",
)
async def update_ai_prompt(
    prompt_id: uuid.UUID,
    body: UpdateAIPromptRequest,
    _admin: AdminDep,
    use_case: AIPromptUseCase = Depends(get_use_case),
) -> ApiResponse[AIPromptResponse]:
    dto = await use_case.update(
        prompt_id=prompt_id,
        system_prompt_template=body.system_prompt_template,
        version=body.version,
    )
    return ApiResponse(data=_to_response(dto))
