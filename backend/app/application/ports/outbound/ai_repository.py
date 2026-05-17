"""
Outbound Port — Repository Interfaces cho AI Workspace.
IDocumentRepository, IChatSessionRepository, IAITaskRepository.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID
from typing import Any

from app.domain.models.ai import Document, ChatSession, ChatMessage, AITask


class IDocumentRepository(ABC):
    """Abstract Port: Contract cho Document (RAG) data access."""

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Document | None: ...

    @abstractmethod
    async def get_by_uploader(self, uploader_id: UUID) -> list[Document]: ...

    @abstractmethod
    async def create(
        self, uploader_id: UUID, filename: str, file_type: str, s3_url: str, **kwargs
    ) -> Document: ...

    @abstractmethod
    async def update_status(self, document: Document, status: str) -> Document: ...

    @abstractmethod
    async def soft_delete(self, document: Document) -> Document: ...


class IChatRepository(ABC):
    """Abstract Port: Contract cho Chat Session & Message data access."""

    @abstractmethod
    async def get_session_by_id(self, session_id: UUID) -> ChatSession | None: ...

    @abstractmethod
    async def get_sessions_by_user(
        self, user_id: UUID, *, limit: int = 20
    ) -> list[ChatSession]:
        """Lấy danh sách sessions của user, sắp xếp theo updated_at DESC."""
        ...

    @abstractmethod
    async def create_session(
        self, user_id: UUID, *, title: str | None = None, ai_persona: str | None = None
    ) -> ChatSession: ...

    @abstractmethod
    async def get_messages(
        self,
        session_id: UUID,
        *,
        limit: int = 20,
        cursor_created_at: "datetime | None" = None,
        ascending: bool = True,
    ) -> list[ChatMessage]:
        """
        Lấy tin nhắn với cursor-based pagination.

        cursor_created_at: created_at của message cuối cùng đã fetch.
        ascending=True (default): scroll xuống, lấy messages CŨ HƠN cursor.
        ascending=False: lấy messages MỚI HƠN cursor (refresh).

        KHÔNG dùng UUID làm cursor vì UUID v4 là random, không sortable theo thời gian.
        """
        ...

    @abstractmethod
    async def add_message(
        self, session_id: UUID, sender_type: str, content: str
    ) -> ChatMessage: ...


class IAITaskRepository(ABC):
    """Abstract Port: Contract cho AI Background Task tracking."""

    @abstractmethod
    async def create(self, user_id: UUID, task_type: str) -> AITask: ...

    @abstractmethod
    async def update_status(
        self,
        task: AITask,
        status: str,
        result_payload: dict[str, Any] | None = None,
    ) -> AITask: ...

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> AITask | None: ...
