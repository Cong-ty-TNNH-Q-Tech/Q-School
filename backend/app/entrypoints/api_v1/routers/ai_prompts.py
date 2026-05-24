"""
Driving Adapter (Primary): AI Prompts Router
Chỉ có nhiệm vụ: nhận HTTP Request → gọi Use Case → trả HTTP Response.
Không chứa bất kỳ business logic nào.
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.ai_prompt_repository import SQLAlchemyAIPromptRepository
from app.application.use_cases.ai_prompt_use_case import AIPromptUseCase
from app.core.database import get_db
from app.core.security import AdminDep
from app.entrypoints.api_v1.schemas.ai_prompt_schemas import (
    AIPromptListResponse,
    AIPromptResponse,
    AIPromptSingleResponse,
    CreateAIPromptRequest,
    UpdateAIPromptRequest,
)

router = APIRouter(prefix="/ai-prompts", tags=["AI Prompts"])


# ------------------------------------------------------------------
# Dependency Factory: inject Use Case với concrete Repository
# ------------------------------------------------------------------


def get_use_case(db: AsyncSession = Depends(get_db)) -> AIPromptUseCase:
    repo = SQLAlchemyAIPromptRepository(db)
    return AIPromptUseCase(repo)


# ------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------


@router.post(
    "",
    response_model=AIPromptSingleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Tạo mới AI Prompt / Persona",
)
async def create_ai_prompt(
    body: CreateAIPromptRequest,
    _admin: dict = Depends(AdminDep),
    use_case: AIPromptUseCase = Depends(get_use_case),
) -> AIPromptSingleResponse:
    dto = await use_case.create(
        persona_name=body.persona_name,
        system_prompt_template=body.system_prompt_template,
        version=body.version,
    )
    return AIPromptSingleResponse(data=AIPromptResponse(**dto.__dict__))


@router.get(
    "",
    response_model=AIPromptListResponse,
    status_code=status.HTTP_200_OK,
    summary="[Admin] Lấy danh sách tất cả AI Prompts",
)
async def list_ai_prompts(
    _admin: dict = Depends(AdminDep),
    use_case: AIPromptUseCase = Depends(get_use_case),
) -> AIPromptListResponse:
    dtos = await use_case.list_all()
    return AIPromptListResponse(data=[AIPromptResponse(**d.__dict__) for d in dtos])


@router.get(
    "/{prompt_id}",
    response_model=AIPromptSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết một AI Prompt theo ID",
)
async def get_ai_prompt(
    prompt_id: uuid.UUID,
    use_case: AIPromptUseCase = Depends(get_use_case),
) -> AIPromptSingleResponse:
    dto = await use_case.get_by_id(prompt_id)
    return AIPromptSingleResponse(data=AIPromptResponse(**dto.__dict__))


@router.patch(
    "/{prompt_id}",
    response_model=AIPromptSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="[Admin] Cập nhật system_prompt_template / version",
)
async def update_ai_prompt(
    prompt_id: uuid.UUID,
    body: UpdateAIPromptRequest,
    _admin: dict = Depends(AdminDep),
    use_case: AIPromptUseCase = Depends(get_use_case),
) -> AIPromptSingleResponse:
    dto = await use_case.update(
        prompt_id=prompt_id,
        system_prompt_template=body.system_prompt_template,
        version=body.version,
    )
    return AIPromptSingleResponse(data=AIPromptResponse(**dto.__dict__))
