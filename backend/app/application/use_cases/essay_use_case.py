import uuid

from app.application.ports.outbound.quiz_repository import IEssaySubmissionRepository
from app.application.ports.outbound.ai_repository import IAITaskRepository
from app.domain.models.quiz import EssaySubmission
from app.domain.models.user import User

class EssayUseCase:
    """
    Use Case cho Essay Submission logic.
    """

    def __init__(
        self, essay_repo: IEssaySubmissionRepository, ai_task_repo: IAITaskRepository
    ) -> None:
        self._essay_repo = essay_repo
        self._ai_task_repo = ai_task_repo

    async def submit_essay(
        self, student: User, teacher_id: uuid.UUID, content: str, rubric_id: uuid.UUID | None = None
    ) -> tuple[EssaySubmission, uuid.UUID]:
        """
        Học sinh nộp bài tự luận.
        Chỉ lưu vào DB và tạo AI Task (trạng thái pending).
        KHÔNG chấm bài đồng bộ. Trả về submission và task_id để trả về HTTP 202.
        """
        submission = await self._essay_repo.create(
            student_id=student.id,
            teacher_id=teacher_id,
            content=content,
            rubric_id=rubric_id
        )

        ai_task = await self._ai_task_repo.create(
            user_id=student.id,
            task_type="essay_grading"
        )
        await self._ai_task_repo.update_status(
            task=ai_task,
            status="pending",
            result_payload={"essay_submission_id": str(submission.id)}
        )

        from app.entrypoints.celery_worker.ai_tasks import process_essay_grading
        
        # Dispatch background task qua Celery
        process_essay_grading.apply_async(
            kwargs={
                "essay_submission_id": str(submission.id),
                "user_id": str(student.id),
                "ai_task_id": str(ai_task.id)
            }
        )

        return submission, ai_task.id

    async def get_essay(self, submission_id: uuid.UUID) -> EssaySubmission | None:
        """
        Lấy thông tin bài tự luận để xem kết quả.
        """
        return await self._essay_repo.get_by_id(submission_id)
