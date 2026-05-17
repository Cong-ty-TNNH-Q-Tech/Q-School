"""
API v1 Router — Tập trung tất cả routers của API v1.
Thêm router mới tại đây khi implement từng nhóm tính năng.
"""
from fastapi import APIRouter

# Import các router khi đã được implement
# from app.entrypoints.api_v1.auth import router as auth_router
# from app.entrypoints.api_v1.users import router as users_router
# from app.entrypoints.api_v1.classes import router as classes_router
# from app.entrypoints.api_v1.lessons import router as lessons_router
# from app.entrypoints.api_v1.quizzes import router as quizzes_router
# from app.entrypoints.api_v1.ai_chat import router as ai_chat_router

api_v1_router = APIRouter(prefix="/api/v1")

# ──────────────────────────────────────────────
# Đăng ký routers — Uncomment khi đã implement
# ──────────────────────────────────────────────
# api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# api_v1_router.include_router(users_router, prefix="/users", tags=["Users"])
# api_v1_router.include_router(classes_router, prefix="/classes", tags=["Classes"])
# api_v1_router.include_router(lessons_router, prefix="/lessons", tags=["Lessons"])
# api_v1_router.include_router(quizzes_router, prefix="/quizzes", tags=["Quizzes"])
# api_v1_router.include_router(ai_chat_router, prefix="/ai", tags=["AI"])
