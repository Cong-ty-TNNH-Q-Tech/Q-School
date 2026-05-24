from fastapi import APIRouter

from app.entrypoints.api_v1.routers.ai_prompts import router as ai_prompts_router

api_v1_router = APIRouter(prefix="/api/v1")

# Đăng ký tất cả routers vào đây
api_v1_router.include_router(ai_prompts_router)
