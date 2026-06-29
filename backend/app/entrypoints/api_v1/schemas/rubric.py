"""
Rubric Pydantic Schemas — Request/Response models cho Rubric endpoints.
Dinh nghia theo openapi.yaml Group: Rubrics.
"""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator, model_validator


# ──────────────────────────────────────────────
# REQUEST SCHEMAS (Input Validation)
# ──────────────────────────────────────────────
class CreateRubricRequest(BaseModel):
    """POST /rubrics — Tao ma tran tieu chi moi."""
    title: str
    criteria_matrix: dict[str, Any]

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tieu de ma tran tieu chi khong duoc de trong")
        if len(v) > 255:
            raise ValueError("Tieu de ma tran tieu chi khong duoc vuot qua 255 ky tu")
        return v

    @field_validator("criteria_matrix")
    @classmethod
    def matrix_not_empty(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not v:
            raise ValueError("Ma tran tieu chi khong duoc de trong")
        return v


class UpdateRubricRequest(BaseModel):
    """PATCH /rubrics/{id} — Cap nhat thong tin ma tran tieu chi."""
    title: str | None = None
    criteria_matrix: dict[str, Any] | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tieu de ma tran tieu chi khong duoc de trong")
            if len(v) > 255:
                raise ValueError("Tieu de ma tran tieu chi khong duoc vuot qua 255 ky tu")
        return v

    @field_validator("criteria_matrix")
    @classmethod
    def matrix_not_empty(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        if v is not None and not v:
            raise ValueError("Ma tran tieu chi khong duoc de trong")
        return v

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UpdateRubricRequest":
        """
        Dam bao PATCH request co it nhat mot field cap nhat co y nghia.
        """
        if not self.model_fields_set or (
            self.title is None
            and self.criteria_matrix is None
        ):
            raise ValueError(
                "Phai cung cap it nhat mot truong can cap nhat (title, criteria_matrix)"
            )
        return self


# ──────────────────────────────────────────────
# RESPONSE SCHEMAS (Output Serialization)
# ──────────────────────────────────────────────
class RubricResponse(BaseModel):
    """
    Thong tin ma tran tieu chi day du.
    Dung cho: tat ca Rubric endpoints.
    """
    id: uuid.UUID
    teacher_id: uuid.UUID
    title: str
    criteria_matrix: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    # Thong tin teacher (eager loaded)
    teacher_name: str | None = None

    model_config = {"from_attributes": True}
