"""
Driven Adapter: SQLAlchemyAIPromptRepository
Implements AIPromptRepository (Port) bằng SQLAlchemy async.
Tầng này là nơi DUY NHẤT được phép dùng SQLAlchemy ORM.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.outbound.ai_prompt_repository import AIPromptRepository
from app.domain.models.ai import AIPrompt


class SQLAlchemyAIPromptRepository(AIPromptRepository):  # pragma: no cover

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, prompt_id: uuid.UUID) -> AIPrompt | None:
        result = await self._session.execute(
            select(AIPrompt).where(AIPrompt.id == prompt_id)
        )
        return result.scalar_one_or_none()

    async def get_by_persona_name(self, persona_name: str) -> AIPrompt | None:
        result = await self._session.execute(
            select(AIPrompt).where(AIPrompt.persona_name == persona_name)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[AIPrompt]:
        result = await self._session.execute(
            select(AIPrompt).order_by(AIPrompt.persona_name)
        )
        return list(result.scalars().all())

    async def create(
        self,
        persona_name: str,
        system_prompt_template: str,
        version: str,
    ) -> AIPrompt:
        prompt = AIPrompt(
            persona_name=persona_name,
            system_prompt_template=system_prompt_template,
            version=version,
        )
        self._session.add(prompt)
        await self._session.commit()
        await self._session.refresh(prompt)
        return prompt

    async def update(
        self,
        prompt_id: uuid.UUID,
        system_prompt_template: str | None,
        version: str | None,
    ) -> AIPrompt | None:
        values: dict = {"updated_at": datetime.now(timezone.utc)}
        if system_prompt_template is not None:
            values["system_prompt_template"] = system_prompt_template
        if version is not None:
            values["version"] = version

        await self._session.execute(
            update(AIPrompt).where(AIPrompt.id == prompt_id).values(**values)
        )
        await self._session.commit()
        return await self.get_by_id(prompt_id)
