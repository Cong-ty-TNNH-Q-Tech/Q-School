"""
Celery Worker — AI Background Task placeholder.
Các tác vụ AI nặng (chấm bài, sinh giáo án) sẽ được implement tại đây.

Pattern chuẩn cho mọi AI Task:
    1. Set AITask.status = 'processing' ngay khi bắt đầu
    2. Thực hiện logic AI
    3. Set AITask.status = 'completed' + lưu result_payload
    4. Nếu lỗi: Set AITask.status = 'failed' + lưu error trong result_payload
"""
import logging
from celery import Task
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


class AIBaseTask(Task):
    """
    Base class cho tất cả AI Celery Tasks.
    Tự động update AITask.status trong DB khi task thất bại.
    Member implement task cụ thể bằng cách kế thừa class này.
    """
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Callback khi task fail — được gọi tự động bởi Celery.
        TODO (member): Update AITask.status = 'failed' trong DB dựa vào task_id.
        """
        logger.error(
            "AI Task FAILED | task_id=%s | error=%s",
            task_id, str(exc), exc_info=einfo
        )

    def on_success(self, retval, task_id, args, kwargs):
        """
        Callback khi task thành công.
        TODO (member): Update AITask.status = 'completed' + lưu retval.
        """
        logger.info("AI Task SUCCESS | task_id=%s", task_id)


@celery_app.task(
    bind=True,
    base=AIBaseTask,
    name="ai_tasks.process_essay_grading",
    max_retries=3,
    default_retry_delay=60,
)
def process_essay_grading(self, essay_submission_id: str, user_id: str) -> dict:
    """
    Background task: Chấm điểm bài văn tự luận bằng AI.

    Flow dự kiến (TODO member implement):
        1. Load EssaySubmission + Rubric từ DB
        2. Gọi ILLMService.generate() với nội dung + rubric
        3. Parse kết quả AI -> ai_feedback JSONB
        4. Update EssaySubmission.score + AITask.status
    """
    logger.info("[essay_grading] START submission=%s", essay_submission_id)
    try:
        # TODO: Implement khi AI pipeline sẵn sàng
        return {"status": "not_implemented", "task_id": self.request.id}
    except Exception as exc:
        logger.error("[essay_grading] FAIL submission=%s error=%s", essay_submission_id, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=AIBaseTask,
    name="ai_tasks.generate_lesson_plan",
    max_retries=3,
    default_retry_delay=60,
)
def generate_lesson_plan(self, ai_task_id: str, prompt_params: dict) -> dict:
    """
    Background task: Sinh giáo án AI.

    Flow dự kiến:
        1. Load AITask + ai_persona từ DB
        2. Gọi ILLMService.generate() với params
        3. Parse output -> Lesson content JSONB
        4. Tạo Lesson mới hoặc update GeneratedAsset
    """
    logger.info("[generate_lesson] START ai_task_id=%s", ai_task_id)
    try:
        # TODO: Implement khi AI pipeline sẵn sàng
        return {"status": "not_implemented", "task_id": self.request.id}
    except Exception as exc:
        logger.error("[generate_lesson] FAIL ai_task_id=%s error=%s", ai_task_id, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=AIBaseTask,
    name="ai_tasks.parse_document",
    max_retries=2,
    default_retry_delay=30,
)
def parse_document(self, document_id: str) -> dict:
    """
    Background task: Parse PDF và tạo vector embeddings cho RAG.

    Flow dự kiến:
        1. Download file từ S3/R2 qua IStorageService
        2. Cắt nhỏ thành chunks
        3. Gọi ILLMService.embed() cho từng chunk
        4. Lưu DocumentChunk records vào DB
        5. Update Document.status = 'ready'
    """
    logger.info("[parse_document] START document_id=%s", document_id)
    try:
        # TODO: Implement khi AI pipeline sẵn sàng
        return {"status": "not_implemented", "task_id": self.request.id}
    except Exception as exc:
        logger.error("[parse_document] FAIL document_id=%s error=%s", document_id, exc)
        raise self.retry(exc=exc)
