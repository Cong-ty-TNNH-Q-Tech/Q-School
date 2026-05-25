"""
Ports — Outbound Port exports (barrel file).
Adapters import từ đây để biết interface nào cần implement.
"""

from app.application.ports.outbound.user_repository import IUserRepository
from app.application.ports.outbound.class_repository import IClassRepository
from app.application.ports.outbound.quiz_repository import (
    IQuizRepository,
    IQuizAttemptRepository,
    IEssaySubmissionRepository,
)
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
    "IQuizRepository",
    "IQuizAttemptRepository",
    "IEssaySubmissionRepository",
    "IDocumentRepository",
    "IChatRepository",
    "IAITaskRepository",
    "ILLMService",
    "IStorageService",
]
