"""
Rubric Pydantic Schemas — Request/Response models.
"""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


class CreateRubricRequest(BaseModel):
    """POST /rubrics"""
    title: str
    criteria_matrix: dict[str, Any]

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 255:
            raise ValueError("Title phải từ 1–255 ký tự")
        return v

    @field_validator("criteria_matrix")
    @classmethod
    def matrix_not_empty(cls, v: dict) -> dict:
        if not v:
            raise ValueError("criteria_matrix không được rỗng")
        return v


class UpdateRubricRequest(BaseModel):
    """PATCH /rubrics/{id}"""
    title: str | None = None
    criteria_matrix: dict[str, Any] | None = None

    @field_validator("title")
    @classmethod
    def title_valid(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v or len(v) > 255:
                raise ValueError("Title phải từ 1–255 ký tự")
        return v

    @field_validator("criteria_matrix")
    @classmethod
    def matrix_valid(cls, v: dict | None) -> dict | None:
        if v is not None and not v:
            raise ValueError("criteria_matrix không được rỗng")
        return v


class RubricOut(BaseModel):
    """Response model cho Rubric."""
    id: uuid.UUID
    teacher_id: uuid.UUID
    title: str
    criteria_matrix: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
