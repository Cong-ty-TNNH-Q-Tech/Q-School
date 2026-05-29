"""
Ports — Top-level barrel file.
Import tất cả ports từ một chỗ duy nhất.
"""

from app.application.ports.inbound import IAuthUseCase, IAIChatUseCase
from app.application.ports.outbound import (
    IUserRepository,
    IClassRepository,
    IQuizRepository,
    IQuizAttemptRepository,
    IEssaySubmissionRepository,
    IDocumentRepository,
    IChatRepository,
    IAITaskRepository,
    ILLMService,
    IStorageService,
)

__all__ = [
    # Inbound
    "IAuthUseCase",
    "IAIChatUseCase",
    # Outbound — Repositories
    "IUserRepository",
    "IClassRepository",
    "IQuizRepository",
    "IQuizAttemptRepository",
    "IEssaySubmissionRepository",
    "IDocumentRepository",
    "IChatRepository",
    "IAITaskRepository",
    # Outbound — Services
    "ILLMService",
    "IStorageService",
]
