from fastapi import APIRouter, Depends, HTTPException, status
from app.entrypoints.api_v1.schemas.youtube import (
    YouTubeQuestionRequest,
    YouTubeTaskResponse,
    YouTubeTaskStatusResponse
)
from app.core.dependencies import AIUserDep
from celery.result import AsyncResult
from app.entrypoints.api_v1.schemas.base import ApiResponse
from app.entrypoints.celery_worker.ai_tasks import generate_youtube_questions_task

router = APIRouter()

@router.post("/youtube-questions", response_model=ApiResponse[YouTubeTaskResponse], status_code=status.HTTP_202_ACCEPTED)
async def create_youtube_questions_task(
    request: YouTubeQuestionRequest,
    current_user: AIUserDep,
):
    """
    Tạo câu hỏi tự động từ video YouTube (Chạy background task).
    Trả về Task ID để polling kết quả.
    """
    task = generate_youtube_questions_task.delay(url=request.url, question_count=request.question_count)
    
    return ApiResponse(
        data=YouTubeTaskResponse(task_id=task.id), 
        message="Task đã được đưa vào hàng đợi"
    )

@router.get("/youtube-questions/{task_id}", response_model=ApiResponse[YouTubeTaskStatusResponse])
async def get_youtube_questions_status(
    task_id: str,
    current_user: AIUserDep,
):
    """
    Kiểm tra trạng thái của task tạo câu hỏi từ YouTube.
    """
    task_result = AsyncResult(task_id)
    
    status_str = "PENDING"
    result_data = None
    error_msg = None
    
    if task_result.state == 'SUCCESS':
        status_str = "COMPLETED"
        result_data = task_result.result
    elif task_result.state == 'FAILURE':
        status_str = "FAILED"
        error_msg = str(task_result.info)
    elif task_result.state in ['STARTED', 'RETRY']:
        status_str = "PROCESSING"
        
    return ApiResponse(
        data=YouTubeTaskStatusResponse(
            task_id=task_id,
            status=status_str,
            result=result_data,
            error=error_msg
        )
    )
