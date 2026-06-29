"""
Outbound Port — Repository Interface cho Rubric.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.domain.models.quiz import Rubric


class IRubricRepository(ABC):
    """Abstract Port: Contract cho Rubric data access."""

    @abstractmethod
    async def get_by_id(self, rubric_id: UUID) -> Rubric | None: ...

    @abstractmethod
    async def get_by_teacher(self, teacher_id: UUID) -> list[Rubric]: ...

    @abstractmethod
    async def create(self, teacher_id: UUID, title: str, criteria_matrix: dict[str, Any], **kwargs) -> Rubric: ...

    @abstractmethod
    async def update(self, rubric: Rubric, **kwargs) -> Rubric: ...

    @abstractmethod
    async def soft_delete(self, rubric: Rubric) -> Rubric: ...
