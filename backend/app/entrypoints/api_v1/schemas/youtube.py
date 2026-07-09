from pydantic import BaseModel, Field
from typing import List

class YouTubeQuestionAnswer(BaseModel):
    text: str
    is_correct: bool

class YouTubeQuestionResponse(BaseModel):
    question_text: str
    timestamp: float = Field(..., description="Thời gian tương ứng trong video (giây)")
    answers: List[YouTubeQuestionAnswer]

class YouTubeQuestionRequest(BaseModel):
    url: str = Field(..., pattern=r"^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})", description="Link video YouTube")
    question_count: int = Field(5, ge=1, le=20, description="Số lượng câu hỏi cần tạo")

class YouTubeTaskResponse(BaseModel):
    task_id: str = Field(..., description="ID của Celery task đang xử lý")

class YouTubeTaskStatusResponse(BaseModel):
    task_id: str
    status: str = Field(..., description="PENDING, PROCESSING, COMPLETED, FAILED")
    result: List[YouTubeQuestionResponse] | None = None
    error: str | None = None
