"""
Outbound Port: AIPromptRepository
Theo Hexagonal Architecture — đây là Interface thuần túy (Abstract Base Class).
Use Case chỉ phụ thuộc vào Port này, không biết gì về SQLAlchemy.
"""

import uuid
from abc import ABC, abstractmethod

from app.domain.models.ai_prompt import AIPrompt


class AIPromptRepository(ABC):

    @abstractmethod
    async def get_by_id(
        self, prompt_id: uuid.UUID
    ) -> AIPrompt | None:  # pragma: no cover
        """Lấy prompt theo ID."""
        ...

    @abstractmethod
    async def get_by_persona_name(
        self, persona_name: str
    ) -> AIPrompt | None:  # pragma: no cover
        """Lấy prompt theo tên persona (VD: 'Raina', 'Tutor')."""
        ...

    @abstractmethod
    async def list_all(self) -> list[AIPrompt]:  # pragma: no cover
        """Trả về danh sách tất cả AI prompts."""
        ...

    @abstractmethod
    async def create(
        self, persona_name: str, system_prompt_template: str, version: str
    ) -> AIPrompt:  # pragma: no cover
        """Tạo mới một AI Prompt."""
        ...

    @abstractmethod
    async def update(  # pragma: no cover
        self,
        prompt_id: uuid.UUID,
        system_prompt_template: str | None,
        version: str | None,
    ) -> AIPrompt | None:
        """Cập nhật system_prompt_template và/hoặc version theo ID."""
        ...
