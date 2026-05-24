"""
Use Case: AIPromptUseCase
Chứa toàn bộ logic nghiệp vụ — không biết gì về HTTP hay Database.
Phụ thuộc hoàn toàn vào AIPromptRepository (Interface).
"""

import uuid
from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException, status

from app.application.ports.outbound.ai_prompt_repository import AIPromptRepository
from app.domain.models.ai import AIPrompt


@dataclass
class AIPromptDTO:
    """Data Transfer Object trả ra ngoài — tách biệt domain model với HTTP layer."""

    id: uuid.UUID
    persona_name: str
    system_prompt_template: str
    version: str
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj: AIPrompt) -> "AIPromptDTO":
        return cls(
            id=obj.id,
            persona_name=obj.persona_name,
            system_prompt_template=obj.system_prompt_template,
            version=obj.version,
            updated_at=obj.updated_at,
        )


class AIPromptUseCase:
    """
    Single-Responsibility: chỉ xử lý logic nghiệp vụ của AI Prompts.
    Inject AIPromptRepository qua constructor (Dependency Inversion).
    """

    def __init__(self, repo: AIPromptRepository) -> None:
        self._repo = repo

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    async def get_by_id(self, prompt_id: uuid.UUID) -> AIPromptDTO:
        prompt = await self._repo.get_by_id(prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy AI Prompt với id={prompt_id}.",
            )
        return AIPromptDTO.from_orm(prompt)

    async def get_by_persona_name(self, persona_name: str) -> AIPromptDTO:
        """Dùng bởi ChatUseCase để lấy system_prompt_template trước khi gọi LLM."""
        prompt = await self._repo.get_by_persona_name(persona_name)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy persona '{persona_name}'.",
            )
        return AIPromptDTO.from_orm(prompt)

    async def list_all(self) -> list[AIPromptDTO]:
        prompts = await self._repo.list_all()
        return [AIPromptDTO.from_orm(p) for p in prompts]

    # ------------------------------------------------------------------
    # WRITE (Admin only — quyền được enforce ở Router layer)
    # ------------------------------------------------------------------

    async def create(
        self,
        persona_name: str,
        system_prompt_template: str,
        version: str,
    ) -> AIPromptDTO:
        # Kiểm tra trùng persona_name
        existing = await self._repo.get_by_persona_name(persona_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Persona '{persona_name}' đã tồn tại. Dùng PATCH để cập nhật.",
            )
        prompt = await self._repo.create(persona_name, system_prompt_template, version)
        return AIPromptDTO.from_orm(prompt)

    async def update(
        self,
        prompt_id: uuid.UUID,
        system_prompt_template: str | None,
        version: str | None,
    ) -> AIPromptDTO:
        # Đảm bảo tồn tại trước khi update
        await self.get_by_id(prompt_id)

        updated = await self._repo.update(prompt_id, system_prompt_template, version)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cập nhật thất bại — không tìm thấy record.",
            )
        return AIPromptDTO.from_orm(updated)
