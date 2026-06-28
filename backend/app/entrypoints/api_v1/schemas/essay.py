from uuid import UUID
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

class EssaySubmissionRequest(BaseModel):
    teacher_id: UUID
    content: str = Field(..., description="Nội dung bài văn tự luận")
    rubric_id: UUID | None = None

class EssaySubmissionResponse(BaseModel):
    id: UUID
    student_id: UUID
    teacher_id: UUID
    rubric_id: UUID | None = None
    content: str
    ai_feedback: dict[str, Any] | None = None
    score: float | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EssaySubmissionAcceptedResponse(BaseModel):
    message: str = "Đã nhận bài và đang tiến hành chấm điểm"
    submission_id: UUID
    ai_task_id: UUID
