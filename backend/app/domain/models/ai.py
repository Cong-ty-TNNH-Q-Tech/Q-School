"""
AI Workspace ORM Models — AIPrompt, ChatSession, ChatMessage,
Document, DocumentChunk (pgvector), AITask, GeneratedAsset
Group 3: AI Workspace & Storage
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base
from app.domain.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.domain.models.user import User


class AIPrompt(Base, UUIDMixin):
    """
    Bảng AI_PROMPTS — Quản lý System Prompts động cho các AI Persona.
    Admin chỉnh sửa qua Web UI, không cần deploy lại Backend.
    """
    __tablename__ = "ai_prompts"

    persona_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True,
        comment="Tên nhân vật AI (VD: Raina, Tutor, StudyBot)"
    )
    system_prompt_template: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Mẫu System Prompt với {placeholder} để inject context"
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1.0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class ChatSession(Base, UUIDMixin, TimestampMixin):
    """
    Bảng CHAT_SESSIONS — Phiên trò chuyện AI.
    document_id: liên kết với PDF để kích hoạt chế độ Chat với tài liệu (RAG).
    """
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True,
        comment="Context RAG: Chat với PDF cụ thể"
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ai_persona: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Soft FK → AIPrompt.persona_name. Không dùng FK thật vì Admin có thể đổi tên persona khi cần."
    )

    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    document: Mapped["Document | None"] = relationship("Document", back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    """
    Bảng CHAT_MESSAGES — Lịch sử tin nhắn.
    IMMUTABLE: Không cho phép sửa/xóa tin nhắn sau khi đã gửi (chỉ soft-delete session).
    Dùng Cursor Pagination (không dùng Offset) khi query.
    sender_type: 'user' | 'ai'
    """
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint("sender_type IN ('user', 'ai')", name="ck_chat_messages_sender_type"),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    sender_type: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="'user' hoặc 'ai'"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")


class Document(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Bảng DOCUMENTS — Metadata file upload (PDF, DOCX, ảnh).
    File thực tế lưu trên S3/R2, chỉ lưu URL ở đây.
    status: 'pending' | 'parsing' | 'ready' | 'error'
    """
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("file_type IN ('pdf', 'docx', 'image')", name="ck_documents_file_type"),
        CheckConstraint("status IN ('pending', 'parsing', 'ready', 'error')", name="ck_documents_status"),
    )

    uploader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="pdf, docx, image")
    s3_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Chia sẻ dùng chung toàn trường"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending",
        comment="pending | parsing | ready | error"
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession", back_populates="document"
    )


class DocumentChunk(Base, UUIDMixin):
    """
    Bảng DOCUMENT_CHUNKS — Vector Embeddings cho RAG.
    HNSW Index bắt buộc phải được tạo trên embedding_vector (xem migration).
    """
    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_vector: Mapped[Any] = mapped_column(
        Vector(1536),
        nullable=True,
        comment="pgvector — HNSW Index BẮTBUỘC trên cột này (xem migration)"
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")


class AITask(Base, UUIDMixin, TimestampMixin):
    """
    Bảng AI_TASKS — Giám sát tiến trình Celery Background Tasks.
    status: 'pending' | 'processing' | 'completed' | 'failed'
    """
    __tablename__ = "ai_tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending",
        index=True,   # Index để query tất cả tasks đang pending/processing hiệu quả
        comment="pending | processing | completed | failed"
    )
    result_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GeneratedAsset(Base, UUIDMixin, TimestampMixin):
    """
    Bảng GENERATED_ASSETS — Gom nhóm tất cả văn bản AI sinh ra.
    asset_type: 'email' | 'iep' | 'behavior_intervention' | 'report_comment' | ...
    Tránh tạo nhiều bảng rời cho từng loại output AI.
    """
    __tablename__ = "generated_assets"

    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    asset_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        comment="email | iep | behavior_intervention | report_comment | lesson_plan | quiz"
    )
    input_params: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="Tham số đầu vào người dùng cung cấp"
    )
    output_content: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="Nội dung AI sinh ra"
    )
