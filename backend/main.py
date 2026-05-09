from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Q-School AI API",
    description="Backend for Q-School LMS powered by AI",
    version="1.0.0"
)

# Cấu hình CORS cho Frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Có thể giới hạn lại tên miền ở Production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Q-School AI Backend is running!",
        "version": "1.0.0"
    }

# Để chạy server ở máy Local (Development):
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
