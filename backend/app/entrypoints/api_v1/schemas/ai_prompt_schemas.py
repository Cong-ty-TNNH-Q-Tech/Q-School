"""
Pydantic Schemas: AI Prompts
Định nghĩa Request/Response theo chuẩn {status, data} của dự án.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# REQUEST SCHEMAS
# ------------------------------------------------------------------


class CreateAIPromptRequest(BaseModel):
    persona_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Raina"],
        description="Tên nhân vật AI — phải là duy nhất trong hệ thống",
    )
    system_prompt_template: str = Field(
        ...,
        min_length=10,
        description="Mẫu System Prompt sẽ truyền vào LLM",
    )
    version: str = Field(
        default="v1.0",
        max_length=20,
        examples=["v1.0"],
        description="Phiên bản prompt",
    )


class UpdateAIPromptRequest(BaseModel):
    """PATCH — tất cả fields đều optional (partial update)."""

    system_prompt_template: str | None = Field(
        default=None,
        min_length=10,
        description="Nội dung System Prompt mới",
    )
    version: str | None = Field(
        default=None,
        max_length=20,
        description="Phiên bản mới (Ví dụ: v2.0)",
    )


# ------------------------------------------------------------------
# RESPONSE SCHEMAS
# ------------------------------------------------------------------


class AIPromptResponse(BaseModel):
    id: uuid.UUID
    persona_name: str
    system_prompt_template: str
    version: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIPromptListResponse(BaseModel):
    status: str = "success"
    data: list[AIPromptResponse]


class AIPromptSingleResponse(BaseModel):
    status: str = "success"
    data: AIPromptResponse
