import uuid
from typing import AsyncIterator
from datetime import datetime

from app.application.ports.outbound.ai_repository import IChatRepository
from app.application.ports.outbound.llm_service import ILLMService
from app.domain.models.ai import ChatSession, ChatMessage
from app.domain.models.user import User


class ChatUseCase:
    """
    Use Case cho AI Chat streaming.
    """

    def __init__(self, chat_repo: IChatRepository, llm_service: ILLMService) -> None:
        self._chat_repo = chat_repo
        self._llm_service = llm_service

    async def create_session(
        self, user: User, title: str | None = None, ai_persona: str | None = None
    ) -> ChatSession:
        return await self._chat_repo.create_session(
            user_id=user.id, title=title, ai_persona=ai_persona
        )

    async def list_sessions(
        self,
        user: User,
        limit: int = 20,
        cursor_updated_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
    ) -> list[ChatSession]:
        return await self._chat_repo.get_sessions_by_user(
            user_id=user.id,
            limit=limit,
            cursor_updated_at=cursor_updated_at,
            cursor_id=cursor_id,
        )

    async def get_messages(
        self,
        session_id: uuid.UUID,
        limit: int = 20,
        cursor_created_at: datetime | None = None,
        ascending: bool = True,
    ) -> list[ChatMessage]:
        # TODO: Cần kiểm tra session_id thuộc về user (authorization)
        # Tuy nhiên logic đó có thể được xử lý ở router layer
        return await self._chat_repo.get_messages(
            session_id=session_id,
            limit=limit,
            cursor_created_at=cursor_created_at,
            ascending=ascending,
        )

    async def send_message(
        self, session: ChatSession, content: str
    ) -> AsyncIterator[str]:
        """
        Lưu tin nhắn người dùng, gọi LLM, stream từng token về client.
        Sau khi kết thúc stream, lưu tin nhắn của AI vào Database.
        """
        import anyio
        
        # 1. Lưu user message và COMMIT ngay lập tức.
        # Đảm bảo tin nhắn user được lưu ngay cả khi stream bị ngắt kết nối giữa chừng.
        await self._chat_repo.add_message(
            session_id=session.id, sender_type="user", content=content
        )
        await self._chat_repo.commit()

        # 2. Lấy lịch sử chat (tối đa 20 tin nhắn gần nhất)
        # Để lấy 20 tin nhắn MỚI NHẤT, phải dùng ascending=False (ORDER BY DESC)
        # Sau đó đảo ngược list để LLM đọc theo thứ tự thời gian (cũ -> mới)
        messages = await self._chat_repo.get_messages(
            session_id=session.id, limit=20, ascending=False
        )
        messages = list(reversed(messages))

        # 3. Format tin nhắn cho LLM
        llm_messages = []
        if session.ai_persona:
            llm_messages.append({"role": "system", "content": session.ai_persona})

        for msg in messages:
            llm_messages.append(
                {"role": "assistant" if msg.sender_type == "ai" else "user", "content": msg.content}
            )

        # 4. Stream phản hồi
        async def stream_and_save() -> AsyncIterator[str]:
            full_content = []
            try:
                async for chunk in self._llm_service.stream_chat(llm_messages):
                    full_content.append(chunk)
                    yield chunk
            finally:
                # Khi stream bị huỷ (client disconnect) hoặc kết thúc thành công, lưu DB
                ai_text = "".join(full_content)
                if ai_text:
                    # Sử dụng anyio.CancelScope(shield=True) để bảo vệ DB operation
                    # không bị huỷ theo khi Request Task bị huỷ
                    with anyio.CancelScope(shield=True):
                        try:
                            await self._chat_repo.add_message(
                                session_id=session.id, sender_type="ai", content=ai_text
                            )
                            await self._chat_repo.commit()
                        except Exception as e:
                            import logging
                            logging.getLogger(__name__).error("Failed to save AI message: %s", e)

        return stream_and_save()
