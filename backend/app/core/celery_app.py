"""
Celery Application — Cấu hình Celery với Redis broker.
Worker xử lý các tác vụ AI nặng (chấm bài, sinh giáo án) không đồng bộ.
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "qschool",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.entrypoints.celery_worker.ai_tasks",  # AI processing tasks
    ],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,

    # Task behavior
    task_track_started=True,
    task_acks_late=True,           # Worker xác nhận sau khi xử lý xong (tránh mất task)
    worker_prefetch_multiplier=1,  # Chỉ lấy 1 task mỗi lần (phù hợp task AI nặng)
    task_reject_on_worker_lost=True,

    # Result expiration
    result_expires=3600,           # Kết quả giữ 1 tiếng trong Redis

    # Retry defaults
    task_max_retries=3,
    task_default_retry_delay=60,   # Thử lại sau 60 giây
)
