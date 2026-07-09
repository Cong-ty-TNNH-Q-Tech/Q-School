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

    def _update_task_status_sync(
        self,
        task_db_id: str | None,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """
        Update AITask.status trong DB bằng SYNC SQLAlchemy.

        Celery on_failure/on_success callbacks chạy trong worker thread không có
        async event loop — buộc phải dùng sync connection (psycopg2, không phải asyncpg).

        task_db_id: UUID string của AITask record trong DB (khác với Celery task_id).
                    Truyền vào qua kwargs['ai_task_id'] khi enqueue task.
        """
        if not task_db_id:
            logger.warning(
                "_update_task_status_sync: không có ai_task_id, bỏ qua DB update"
            )
            return

        try:
            from sqlalchemy import create_engine, text
            from app.core.config import settings

            # Dùng SYNC URL (psycopg2) — không dùng asyncpg trong sync context
            sync_engine = create_engine(settings.SYNC_DATABASE_URL, pool_pre_ping=True)
            with sync_engine.begin() as conn:
                result_payload = None
                if error_message:
                    import json

                    result_payload = json.dumps({"error": error_message})

                conn.execute(
                    text(
                        "UPDATE ai_tasks SET status = :status, "
                        "result_payload = COALESCE(:payload::jsonb, result_payload), "
                        "updated_at = now(), "
                        "completed_at = CASE WHEN :status IN ('completed', 'failed') THEN now() ELSE completed_at END "
                        "WHERE id = :id"
                    ),
                    {"status": status, "payload": result_payload, "id": task_db_id},
                )
            sync_engine.dispose()
        except Exception as db_err:
            # Không raise — tránh gây ra infinite loop retry chỉ vì DB update fail
            logger.error("_update_task_status_sync FAILED: %s", db_err)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Callback khi task fail — được gọi tự động bởi Celery.
        Update AITask.status = 'failed' trong DB ngay lập tức.
        """
        logger.error(
            "AI Task FAILED | celery_task_id=%s | ai_task_id=%s | error=%s",
            task_id,
            kwargs.get("ai_task_id"),
            str(exc),
            exc_info=einfo,
        )
        # Update DB — task bị stuck 'processing' nếu không có dòng này
        self._update_task_status_sync(
            task_db_id=kwargs.get("ai_task_id"),
            status="failed",
            error_message=str(exc),
        )

    def on_success(self, retval, task_id, args, kwargs):
        """
        Callback khi task thành công.
        Log kết quả — AI Task DB status đã được update bởi task logic cụ thể.
        """
        logger.info(
            "AI Task SUCCESS | celery_task_id=%s | ai_task_id=%s",
            task_id,
            kwargs.get("ai_task_id"),
        )


@celery_app.task(
    bind=True,
    base=AIBaseTask,
    name="ai_tasks.process_essay_grading",
    max_retries=3,
    default_retry_delay=60,
)
def process_essay_grading(
    self, essay_submission_id: str, user_id: str, *, ai_task_id: str | None = None
) -> dict:
    """
    Background task: Chấm điểm bài văn tự luận bằng AI.
    ai_task_id: UUID của AITask record trong DB (dùng cho on_failure DB update)

    Flow dự kiến (TODO member implement):
        1. Kiểm tra idempotency: nếu AITask.status == 'completed', return luôn
        2. Update AITask.status = 'processing'
        3. Load EssaySubmission + Rubric từ DB
        4. Gọi ILLMService.generate() với nội dung + rubric
        5. Parse kết quả AI -> ai_feedback JSONB
        6. Update EssaySubmission.score + AITask.status = 'completed'
    """
    logger.info(
        "[essay_grading] START submission=%s ai_task_id=%s",
        essay_submission_id,
        ai_task_id,
    )
    try:
        # TODO: Implement khi AI pipeline sẵn sàng.
        # QUAN TRọNG: Kiểm tra idempotency trước khi chạy:
        #   result = db.execute("SELECT status FROM ai_tasks WHERE id = :id", {"id": ai_task_id})
        #   if result.status == 'completed': return {"status": "already_completed"}
        return {"status": "not_implemented", "task_id": self.request.id}
    except Exception as exc:
        logger.error(
            "[essay_grading] FAIL submission=%s error=%s", essay_submission_id, exc
        )
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


async def _run_generate_asset_async(
    asset_id: str,
    creator_id: str,
    asset_type: str,
    input_params: dict,
) -> dict:
    import uuid
    from app.core.database import AsyncSessionFactory
    from app.adapters.database.generated_asset_repository import SQLAlchemyGeneratedAssetRepository
    from app.application.use_cases.generated_asset_use_case import GeneratedAssetUseCase
    from openai import AsyncOpenAI
    from app.core.config import settings

    async with AsyncSessionFactory() as session:
        try:
            repo = SQLAlchemyGeneratedAssetRepository(session)
            # Khởi tạo OpenAI client
            llm = AsyncOpenAI(
                api_key=settings.VLLM_API_KEY,
                base_url=settings.VLLM_API_URL,
            )

            use_case = GeneratedAssetUseCase(repo=repo, llm_client=llm)

            # Gọi logic sinh prompt + gọi LLM
            output_content = await use_case.execute_generation(asset_type, input_params)

            # Cập nhật asset trong DB
            asset = await repo.get_by_id(uuid.UUID(asset_id))
            if asset:
                asset.output_content = output_content
                await session.commit()

            return {"status": "success", "asset_id": asset_id}
        except Exception as exc:
            await session.rollback()
            logger.error("[generate_asset] Async run failed: %s", exc)
            raise exc


async def _update_asset_error_async(asset_id: str, error_msg: str) -> None:
    import uuid
    from app.core.database import AsyncSessionFactory
    from app.adapters.database.generated_asset_repository import SQLAlchemyGeneratedAssetRepository

    async with AsyncSessionFactory() as session:
        try:
            repo = SQLAlchemyGeneratedAssetRepository(session)
            asset = await repo.get_by_id(uuid.UUID(asset_id))
            if asset:
                asset.output_content = {"error": f"AI generation failed: {error_msg}"}
                await session.commit()
        except Exception as db_err:
            await session.rollback()
            logger.error("[generate_asset] Failed to write error to DB: %s", db_err)


@celery_app.task(
    bind=True,
    base=AIBaseTask,
    name="ai_tasks.generate_asset",
    max_retries=3,
    default_retry_delay=60,
)
def generate_asset_task(
    self,
    asset_id: str,
    creator_id: str,
    asset_type: str,
    input_params: dict,
) -> dict:
    """
    Background task: Sinh nội dung AI cho Generated Asset và cập nhật vào DB.
    """
    logger.info("[generate_asset] START asset_id=%s", asset_id)
    import asyncio
    try:
        return asyncio.run(
            _run_generate_asset_async(asset_id, creator_id, asset_type, input_params)
        )
    except Exception as exc:
        logger.error("[generate_asset] Task failed, writing error to DB: %s", exc)
        try:
            asyncio.run(_update_asset_error_async(asset_id, str(exc)))
        except Exception as db_err:
            logger.error("[generate_asset] Error handling failed: %s", db_err)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=AIBaseTask,
    name="ai_tasks.generate_youtube_questions",
    max_retries=2,
    default_retry_delay=60,
)
def generate_youtube_questions_task(self, url: str, question_count: int) -> list[dict]:
    """
    Background task: Tạo câu hỏi trắc nghiệm từ video YouTube.
    """
    logger.info("[generate_youtube_questions] START url=%s", url)
    import asyncio
    from app.adapters.llm_client.vllm_adapter import VLLMAdapter
    from app.adapters.youtube_transcript_adapter import YouTubeTranscriptAdapter
    from app.application.use_cases.youtube_questions_use_case import GenerateVideoQuestionsUseCase

    async def _run():
        youtube_adapter = YouTubeTranscriptAdapter()
        llm = VLLMAdapter()
        use_case = GenerateVideoQuestionsUseCase(youtube_adapter=youtube_adapter, llm_service=llm)
        try:
            results = await use_case.execute(url=url, question_count=question_count)
            return results
        finally:
            await llm.close()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("[generate_youtube_questions] Task failed: %s", exc)
        raise self.retry(exc=exc)

