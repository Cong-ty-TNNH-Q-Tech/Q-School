import uuid
from datetime import datetime
from typing import Annotated
import asyncio

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.dependencies import DbDep, AIUserDep
from app.entrypoints.api_v1.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageCreate,
    ChatMessageListResponse,
    ChatMessageResponse,
)
from app.adapters.database.chat_repository import ChatSQLAlchemyRepository
from app.adapters.llm_client.vllm_adapter import VLLMAdapter
from app.application.use_cases.chat_use_case import ChatUseCase

router = APIRouter(prefix="/chat", tags=["AI Chat"])


def get_chat_use_case(db: DbDep) -> ChatUseCase:
    chat_repo = ChatSQLAlchemyRepository(db)
    # Cấu hình VLLMAdapter với model generation mặc định từ biến môi trường
    # Trong thực tế, VLLMAdapter có thể lấy cấu hình từ Settings
    llm_service = VLLMAdapter()
    return ChatUseCase(chat_repo=chat_repo, llm_service=llm_service)


ChatUseCaseDep = Annotated[ChatUseCase, Depends(get_chat_use_case)]


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_chat_session(
    payload: ChatSessionCreate,
    user: AIUserDep,
    use_case: ChatUseCaseDep,
):
    """Tạo mới một AI Chat Session."""
    return await use_case.create_session(
        user=user, title=payload.title, ai_persona=payload.ai_persona
    )


@router.get("/sessions", response_model=ChatSessionListResponse)
async def get_chat_sessions(
    user: AIUserDep,
    use_case: ChatUseCaseDep,
    limit: int = Query(20, ge=1, le=100),
    cursor_updated_at: datetime | None = Query(None),
    cursor_id: uuid.UUID | None = Query(None),
):
    """
    Lấy danh sách chat sessions của user (Composite Cursor Pagination).
    Sắp xếp theo updated_at giảm dần (Mới nhất lên đầu).
    """
    sessions = await use_case.list_sessions(
        user=user,
        limit=limit,
        cursor_updated_at=cursor_updated_at,
        cursor_id=cursor_id,
    )
    
    next_updated_at = None
    next_id = None
    if len(sessions) == limit:
        next_updated_at = sessions[-1].updated_at
        next_id = sessions[-1].id

    return ChatSessionListResponse(
        data=sessions,
        next_cursor_updated_at=next_updated_at,
        next_cursor_id=next_id,
    )


@router.get("/sessions/{session_id}/messages", response_model=ChatMessageListResponse)
async def get_chat_messages(
    session_id: uuid.UUID,
    user: AIUserDep,
    use_case: ChatUseCaseDep,
    db: DbDep,
    limit: int = Query(20, ge=1, le=100),
    cursor_created_at: datetime | None = Query(None),
    ascending: bool = Query(True),
):
    """
    Lấy tin nhắn trong một session (Cursor Pagination).
    ascending=True: Lấy các tin nhắn CŨ hơn cursor_created_at (Scroll up lịch sử).
    ascending=False: Lấy các tin nhắn MỚI hơn cursor_created_at (Refresh).
    """
    # 1. Verify session belongs to user
    chat_repo = ChatSQLAlchemyRepository(db)
    session = await chat_repo.get_session_by_id(session_id)
    if not session or session.user_id != user.id:
        raise NotFoundException("Chat session not found")

    messages = await use_case.get_messages(
        session_id=session_id,
        limit=limit,
        cursor_created_at=cursor_created_at,
        ascending=ascending,
    )

    next_created_at = None
    if len(messages) == limit:
        next_created_at = messages[-1].created_at

    return ChatMessageListResponse(
        data=messages,
        next_cursor_created_at=next_created_at,
    )


@router.post("/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: uuid.UUID,
    payload: ChatMessageCreate,
    user: AIUserDep,
    use_case: ChatUseCaseDep,
    db: DbDep,
):
    """
    Gửi tin nhắn lên session và nhận phản hồi AI qua Server-Sent Events (SSE Streaming).
    KHÔNG sử dụng WebSocket. Trả về text/event-stream.
    """
    # 1. Verify session belongs to user
    chat_repo = ChatSQLAlchemyRepository(db)
    session = await chat_repo.get_session_by_id(session_id)
    if not session or session.user_id != user.id:
        raise NotFoundException("Chat session not found")

    # 2. Get the stream generator
    stream_generator = await use_case.send_message(
        session=session, content=payload.content
    )

    # 3. Format as SSE text/event-stream
    async def sse_format():
        try:
            async for chunk in stream_generator:
                # SSE format: "data: chunk\n\n"
                # Replacing newline so it doesn't break SSE framing
                formatted_chunk = chunk.replace("\\n", "\\n")
                yield f"data: {formatted_chunk}\n\n"
        except asyncio.CancelledError:
            # Client disconnects early
            raise

    return StreamingResponse(sse_format(), media_type="text/event-stream")
