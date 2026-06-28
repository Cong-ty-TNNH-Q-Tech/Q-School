from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ChatSessionBase(BaseModel):
    title: str | None = None
    ai_persona: str | None = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionListResponse(BaseModel):
    data: list[ChatSessionResponse]
    next_cursor_updated_at: datetime | None = None
    next_cursor_id: UUID | None = None


class ChatMessageBase(BaseModel):
    sender_type: str = Field(..., description="'user' or 'ai'")
    content: str


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(ChatMessageBase):
    id: UUID
    session_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageListResponse(BaseModel):
    data: list[ChatMessageResponse]
    next_cursor_created_at: datetime | None = None
