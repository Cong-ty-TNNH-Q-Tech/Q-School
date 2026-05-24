import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AIPrompt(Base):
    """
    Domain Model: AI_PROMPTS
    Bảng quản lý System Prompts động — Admin có thể cập nhật
    AI Persona qua Web UI mà không cần deploy lại Backend.
    """

    __tablename__ = "ai_prompts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    persona_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Tên nhân vật AI (Ví dụ: Raina, Tutor, StudyBot)",
    )
    system_prompt_template: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mẫu chỉ thị hệ thống sẽ truyền vào LLM",
    )
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="v1.0",
        comment="Phiên bản prompt (Ví dụ: v1.0, v2.1)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
