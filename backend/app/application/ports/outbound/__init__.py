"""
Ports — Outbound Port exports (barrel file).
Adapters import từ đây để biết interface nào cần implement.
"""

from app.application.ports.outbound.user_repository import IUserRepository
from app.application.ports.outbound.class_repository import IClassRepository
from app.application.ports.outbound.lesson_repository import ILessonRepository
from app.application.ports.outbound.quiz_repository import (
    IQuizRepository,
    IQuizAttemptRepository,
)
from app.application.ports.outbound.essay_repository import IEssaySubmissionRepository
from app.application.ports.outbound.rubric_repository import IRubricRepository
from app.application.ports.outbound.ai_repository import (
    IDocumentRepository,
    IChatRepository,
    IAITaskRepository,
)
from app.application.ports.outbound.llm_service import ILLMService
from app.application.ports.outbound.storage_service import IStorageService

__all__ = [
    "IUserRepository",
    "IClassRepository",
    "ILessonRepository",
    "IQuizRepository",
    "IQuizAttemptRepository",
    "IEssaySubmissionRepository",
    "IRubricRepository",
    "IDocumentRepository",
    "IChatRepository",
    "IAITaskRepository",
    "ILLMService",
    "IStorageService",
]
