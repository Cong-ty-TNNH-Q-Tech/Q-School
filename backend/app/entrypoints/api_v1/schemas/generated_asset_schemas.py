"""
Pydantic V2 Schemas cho Generated Assets.
Request / Response models cho API endpoints.
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

ASSET_TYPE = Literal[
    "lesson_plan",
    "quiz",
    "email",
    "iep",
    "behavior_intervention",
    "report_comment",
]


# ── Request Schemas ───────────────────────────────────────────────────────────


class CreateAssetRequest(BaseModel):
    """Request body để tạo mới một Generated Asset."""

    asset_type: ASSET_TYPE = Field(
        ...,
        description="Loại nội dung AI cần tạo",
        examples=["email"],
    )
    input_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Tham số đầu vào (JSONB). VD: {'student_name': 'Minh', 'subject': 'Toán'}",
    )


# ── Response Schemas ──────────────────────────────────────────────────────────


class GeneratedAssetOut(BaseModel):
    """Schema trả về cho một Generated Asset."""

    id: uuid.UUID
    creator_id: uuid.UUID
    asset_type: str
    input_params: dict[str, Any]
    output_content: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
