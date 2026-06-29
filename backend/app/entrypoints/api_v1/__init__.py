"""
API v1 Router — Tập trung tất cả routers của API v1.

PATTERN CHO MEMBER khi thêm router mới:
  1. Tạo file: app/entrypoints/api_v1/<feature>.py
  2. Import router ở đây
  3. api_v1_router.include_router(your_router, prefix="/<feature>", tags=["<Tag>"])
  4. Cập nhật docs/api/openapi.yaml nếu API chưa có trong spec
"""

from fastapi import APIRouter

# ── Group 1: Auth & Users ──────────────────────
from app.entrypoints.api_v1.auth import router as auth_router

# ── Group 2: EdTech Core ────────────────────────
from app.entrypoints.api_v1.classes import router as classes_router
from app.entrypoints.api_v1.lessons import router as lessons_router

# ── Group 3: Student Tracking ──────────────────
# from app.entrypoints.api_v1.quizzes import router as quizzes_router
# from app.entrypoints.api_v1.essays import router as essays_router
# from app.entrypoints.api_v1.flashcards import router as flashcards_router

# ── Group 4: AI Workspace ──────────────────────
from app.entrypoints.api_v1.ai_chat import router as ai_chat_router
# from app.entrypoints.api_v1.documents import router as documents_router
from app.entrypoints.api_v1.routers.generated_assets import (
    router as assets_router,
)  # Issue #113

# ── Group 5: Billing ───────────────────────────
from app.entrypoints.api_v1.billing import router as billing_router, webhook_router


api_v1_router = APIRouter(prefix="/api/v1")

# ── Registered Routers ─────────────────────────
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Uncomment khi member implement từng nhóm:
api_v1_router.include_router(classes_router, prefix="/classes", tags=["Classes"])
api_v1_router.include_router(lessons_router, prefix="/lessons", tags=["Lessons"])
# api_v1_router.include_router(quizzes_router, prefix="/quizzes", tags=["Student Tracking"])
# api_v1_router.include_router(essays_router, prefix="/essays", tags=["Student Tracking"])
# api_v1_router.include_router(flashcards_router, prefix="/flashcard-sets", tags=["Student Tracking"])
api_v1_router.include_router(ai_chat_router)
# api_v1_router.include_router(documents_router, prefix="/documents", tags=["AI Workspace"])
api_v1_router.include_router(
    assets_router, prefix="/generated-assets", tags=["Generated Assets"]
)  # Issue #113
api_v1_router.include_router(billing_router)
api_v1_router.include_router(webhook_router)
