"""
Outbound Port — Repository Interface cho Lesson.

Principle (ISP — Interface Segregation):
  Chi khai bao nhung method ma LessonUseCase thuc su goi qua interface nay.
  Lesson don gian hon Class (khong co bang trung gian), nen interface ngan gon.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.lesson import Lesson


class ILessonRepository(ABC):
    """Abstract Port: Contract cho Lesson data access."""

    @abstractmethod
    async def get_by_id(self, lesson_id: UUID) -> Lesson | None: ...

    @abstractmethod
    async def get_by_teacher(self, teacher_id: UUID) -> list[Lesson]: ...

    @abstractmethod
    async def create(self, teacher_id: UUID, title: str, **kwargs) -> Lesson: ...

    @abstractmethod
    async def update(self, lesson: Lesson, **kwargs) -> Lesson: ...

    @abstractmethod
    async def soft_delete(self, lesson: Lesson) -> Lesson: ...
