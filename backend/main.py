"""
Q-School AI — FastAPI Application Entry Point
Hexagonal Architecture: Driving Adapters (REST + SSE) gọi vào Core Domain.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.entrypoints.api_v1 import api_v1_router


# ──────────────────────────────────────────────
# Application Lifespan (startup / shutdown)
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events:
    - Startup: Kiểm tra kết nối DB, khởi tạo resources
    - Shutdown: Đóng connections
    """
    # STARTUP
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # TODO: Ping DB, ping Redis khi các services sẵn sàng

    yield

    # SHUTDOWN
    print(f"🛑 Shutting down {settings.APP_NAME}")


# ──────────────────────────────────────────────
# FastAPI Application
# ──────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-native EdTech Platform — LMS + AI Workspace",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,      # Tắt Swagger trên Production
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ──────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Exception Handlers
# ──────────────────────────────────────────────
register_exception_handlers(app)

# ──────────────────────────────────────────────
# Routers
# ──────────────────────────────────────────────
app.include_router(api_v1_router)


# ──────────────────────────────────────────────
# Health Check (luôn public, không cần auth)
# ──────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "success",
        "data": {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        },
        "message": "Service is healthy",
        "error_code": 0,
    }


@app.get("/", include_in_schema=False)
async def root():
    return {"status": "success", "message": f"{settings.APP_NAME} is running!"}


# ──────────────────────────────────────────────
# Dev server (chỉ dùng ở local, không dùng ở production)
# Production: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
