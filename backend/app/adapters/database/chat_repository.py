from datetime import datetime
from uuid import UUID

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.ai_repository import IChatRepository
from app.domain.models.ai import ChatSession, ChatMessage


class ChatSQLAlchemyRepository(BaseRepository[ChatSession], IChatRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(ChatSession, db)
        self._message_repo = BaseRepository(ChatMessage, db)

    async def get_session_by_id(self, session_id: UUID) -> ChatSession | None:
        return await self.get_by_id(session_id)

    async def get_sessions_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 20,
        cursor_updated_at: datetime | None = None,
        cursor_id: UUID | None = None,
    ) -> list[ChatSession]:
        stmt = select(ChatSession).where(ChatSession.user_id == user_id)

        # Soft delete filter
        if hasattr(ChatSession, "deleted_at"):
            stmt = stmt.where(ChatSession.deleted_at.is_(None))

        # Cursor pagination via updated_at (DESC)
        if cursor_updated_at is not None:
            if cursor_id is not None:
                stmt = stmt.where(
                    or_(
                        ChatSession.updated_at < cursor_updated_at,
                        and_(
                            ChatSession.updated_at == cursor_updated_at,
                            ChatSession.id < cursor_id,
                        ),
                    )
                )
            else:
                stmt = stmt.where(ChatSession.updated_at < cursor_updated_at)

        stmt = stmt.order_by(ChatSession.updated_at.desc(), ChatSession.id.desc()).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_session(
        self, user_id: UUID, *, title: str | None = None, ai_persona: str | None = None
    ) -> ChatSession:
        return await self.create(user_id=user_id, title=title, ai_persona=ai_persona)

    async def get_messages(
        self,
        session_id: UUID,
        *,
        limit: int = 20,
        cursor_created_at: datetime | None = None,
        ascending: bool = True,
    ) -> list[ChatMessage]:
        # Tái sử dụng cursor_paginate của BaseRepository cho ChatMessage
        messages = await self._message_repo.cursor_paginate(
            cursor_created_at=cursor_created_at,
            cursor_id=None, # Tạm không dùng cursor_id cho messages để đơn giản hoặc truyền qua kwargs nếu cần
            limit=limit,
            filters=[ChatMessage.session_id == session_id],
            ascending=ascending,
        )
        return list(messages)

    async def add_message(
        self, session_id: UUID, sender_type: str, content: str
    ) -> ChatMessage:
        return await self._message_repo.create(
            session_id=session_id, sender_type=sender_type, content=content
        )
