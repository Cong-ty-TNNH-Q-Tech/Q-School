"""
Lesson Pydantic Schemas — Request/Response models cho Lesson endpoints.
Dinh nghia theo openapi.yaml Group 2: EdTech Core / Lessons.

NOTE: Dung model_validate() (Pydantic v2) thay vi from_orm() (deprecated).
"""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator, model_validator


# ──────────────────────────────────────────────
# REQUEST SCHEMAS (Input Validation)
# ──────────────────────────────────────────────
class CreateLessonRequest(BaseModel):
    """POST /lessons — Tao bai giang moi."""
    title: str
    subject: str | None = None
    grade_level: str | None = None
    content: dict[str, Any] | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tieu de bai giang khong duoc de trong")
        if len(v) > 500:
            raise ValueError("Tieu de bai giang khong duoc vuot qua 500 ky tu")
        return v

    @field_validator("subject")
    @classmethod
    def subject_valid(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) > 100:
            raise ValueError("subject khong duoc vuot qua 100 ky tu")
        return v.strip() or None if v is not None else None

    @field_validator("grade_level")
    @classmethod
    def grade_level_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if len(v) > 20:
            raise ValueError("grade_level khong duoc vuot qua 20 ky tu")
        return v or None


class UpdateLessonRequest(BaseModel):
    """PATCH /lessons/{id} — Cap nhat thong tin bai giang (partial update)."""
    title: str | None = None
    subject: str | None = None
    grade_level: str | None = None
    content: dict[str, Any] | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tieu de bai giang khong duoc de trong")
            if len(v) > 500:
                raise ValueError("Tieu de bai giang khong duoc vuot qua 500 ky tu")
        return v

    @field_validator("subject")
    @classmethod
    def subject_valid(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) > 100:
            raise ValueError("subject khong duoc vuot qua 100 ky tu")
        return v.strip() or None if v is not None else None

    @field_validator("grade_level")
    @classmethod
    def grade_level_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if len(v) > 20:
            raise ValueError("grade_level khong duoc vuot qua 20 ky tu")
        return v or None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UpdateLessonRequest":
        """
        Dam bao PATCH request co it nhat mot field cap nhat co y nghia.
        """
        if not self.model_fields_set or (
            self.title is None
            and self.subject is None
            and self.grade_level is None
            and self.content is None
        ):
            raise ValueError(
                "Phai cung cap it nhat mot truong can cap nhat (title, subject, grade_level, hoac content)"
            )
        return self


# ──────────────────────────────────────────────
# RESPONSE SCHEMAS (Output Serialization)
# ──────────────────────────────────────────────
class LessonOut(BaseModel):
    """
    Thong tin bai giang day du.
    Dung cho: tat ca Lesson endpoints.
    """
    id: uuid.UUID
    teacher_id: uuid.UUID | None
    title: str
    subject: str | None
    grade_level: str | None
    content: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    # Thong tin teacher (eager loaded)
    teacher_name: str | None = None

    model_config = {"from_attributes": True}
