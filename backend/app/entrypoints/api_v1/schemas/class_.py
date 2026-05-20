"""
Class Pydantic Schemas — Request/Response models cho Class endpoints.
Định nghĩa theo openapi.yaml Group 2: EdTech Core / Classes.

NOTE: Dùng model_validate() (Pydantic v2) thay vì from_orm() (deprecated).
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator


# ──────────────────────────────────────────────
# REQUEST SCHEMAS (Input Validation)
# ──────────────────────────────────────────────
class CreateClassRequest(BaseModel):
    """POST /classes — Tạo lớp học mới."""
    name: str
    grade_level: str | None = None
    subject: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tên lớp không được để trống")
        if len(v) > 255:
            raise ValueError("Tên lớp không được vượt quá 255 ký tự")
        return v

    @field_validator("grade_level")
    @classmethod
    def grade_level_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if len(v) > 20:
            raise ValueError("grade_level không được vượt quá 20 ký tự")
        return v or None

    @field_validator("subject")
    @classmethod
    def subject_valid(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) > 100:
            raise ValueError("subject không được vượt quá 100 ký tự")
        return v.strip() if v else None


class UpdateClassRequest(BaseModel):
    """PATCH /classes/{id} — Cập nhật thông tin lớp học (partial update)."""
    name: str | None = None
    grade_level: str | None = None
    subject: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tên lớp không được để trống")
            if len(v) > 255:
                raise ValueError("Tên lớp không được vượt quá 255 ký tự")
        return v

    @field_validator("grade_level")
    @classmethod
    def grade_level_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if len(v) > 20:
            raise ValueError("grade_level không được vượt quá 20 ký tự")
        return v or None

    @field_validator("subject")
    @classmethod
    def subject_valid(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) > 100:
            raise ValueError("subject không được vượt quá 100 ký tự")
        return v.strip() if v else None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UpdateClassRequest":
        """
        Đảm bảo PATCH request có ít nhất một field cập nhật có ý nghĩa.

        Hai trường hợp cần reject:
          1. Body rỗng hoàn toàn: {} → model_fields_set = set()
          2. Tất cả field gửi lên đều là null: {"name": null} →
             model_fields_set = {"name"} nhưng sau validation name = None.

        Dùng model_fields_set (check case 1) VÀ all-None (check case 2).
        Chỉ dùng model_fields_set là SAI — {"name": null} sẽ pass qua.
        Chỉ dùng all-None là đủ, nhưng gộp cả hai để rõ intent.
        """
        if not self.model_fields_set or (
            self.name is None and self.grade_level is None and self.subject is None
        ):
            raise ValueError(
                "Phải cung cấp ít nhất một trường cần cập nhật (name, grade_level, hoặc subject)"
            )
        return self


class EnrollStudentRequest(BaseModel):
    """POST /classes/{id}/students — Thêm học sinh vào lớp."""
    student_id: uuid.UUID


# ──────────────────────────────────────────────
# RESPONSE SCHEMAS (Output Serialization)
# ──────────────────────────────────────────────
class ClassStudentOut(BaseModel):
    """Thông tin học sinh trong lớp (từ bảng ClassStudent)."""
    student_id: uuid.UUID
    joined_at: datetime

    # Thông tin User của học sinh (eager loaded)
    username: str | None = None
    email: str | None = None

    model_config = {"from_attributes": True}


class ClassOut(BaseModel):
    """
    Thông tin lớp học đầy đủ.
    Dùng cho: tất cả GET /classes endpoints.
    """
    id: uuid.UUID
    teacher_id: uuid.UUID | None
    name: str
    grade_level: str | None
    subject: str | None
    created_at: datetime
    updated_at: datetime

    # Số lượng học sinh (computed từ len(students))
    student_count: int = 0

    model_config = {"from_attributes": True}


class ClassDetailOut(ClassOut):
    """
    Thông tin lớp học chi tiết — bao gồm danh sách học sinh.
    Dùng cho: GET /classes/{id}.
    """
    students: list[ClassStudentOut] = []
