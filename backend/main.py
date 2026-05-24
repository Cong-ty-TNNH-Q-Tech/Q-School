from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.entrypoints.api_v1.router import api_v1_router

# Import models để SQLAlchemy nhận diện metadata khi create_all
import app.domain.models.ai_prompt  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Tạo bảng tự động khi khởi động (development). Production dùng Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Q-School AI API",
    description="Backend for Q-School LMS powered by AI",
    version="1.0.0",
    lifespan=lifespan,
)

# Cấu hình CORS cho Frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Giới hạn tên miền ở Production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "success",
        "message": "Q-School AI Backend is running!",
        "version": "1.0.0",
    }


# Mount tất cả API v1 routes
app.include_router(api_v1_router)

# Để chạy server ở máy Local (Development):
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
