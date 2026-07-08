from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class StudentAnswerResponse(BaseModel):
    question_id: UUID
    selected_answer_id: UUID | None = None
    is_correct: bool | None = None

class QuizAttemptResponse(BaseModel):
    id: UUID
    student_id: UUID
    quiz_id: UUID
    score: float | None = None
    started_at: datetime
    completed_at: datetime | None = None
    student_answers: list[StudentAnswerResponse] = []

    model_config = ConfigDict(from_attributes=True)

class SubmitAttemptRequest(BaseModel):
    answers: dict[UUID, UUID] = Field(..., description="Mapping from question_id to selected_answer_id")
