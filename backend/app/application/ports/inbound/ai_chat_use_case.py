"""
Inbound Port — AI Chat Use Case Interface.
Router SSE gọi interface này để stream chat response.
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from uuid import UUID


class IAIChatUseCase(ABC):
    """Abstract Inbound Port: Contract cho AI Chat."""

    @abstractmethod
    async def stream_message(
        self,
        user_id: UUID,
        content: str,
        *,
        session_id: UUID | None = None,
        document_id: UUID | None = None,
        ai_persona: str | None = None,
    ) -> AsyncIterator[str]:
        """
        Stream phản hồi AI theo từng token (Server-Sent Events).
        Tự động tạo session mới nếu session_id là None.
        Kích hoạt RAG nếu document_id được cung cấp.
        Raise TooManyRequestsException nếu vượt rate limit.
        Raise PaymentRequiredException nếu hết lượt gói Free.
        """
        ...

    @abstractmethod
    async def get_history(
        self,
        session_id: UUID,
        user_id: UUID,
        *,
        limit: int = 20,
        cursor: UUID | None = None,
    ) -> list[dict]:
        """
        Lấy lịch sử tin nhắn (Cursor Pagination).
        Return: list[dict] — mỗi item là ChatMessage dict:
            {"id": UUID, "sender_type": "user"|"ai", "content": str, "created_at": datetime}
        Raise ForbiddenException nếu user_id không phải chủ session.
        """
        ...
