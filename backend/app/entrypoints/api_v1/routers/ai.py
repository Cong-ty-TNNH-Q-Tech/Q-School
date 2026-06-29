from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.entrypoints.api_v1.schemas.youtube import YouTubeQuestionRequest, YouTubeQuestionResponse
from app.application.use_cases.youtube_questions_use_case import GenerateVideoQuestionsUseCase
from app.adapters.youtube_transcript_adapter import YouTubeTranscriptAdapter
from app.adapters.llm_client.llm_factory import get_llm_service
from app.core.dependencies import CurrentUserDep

from app.entrypoints.api_v1.schemas.base import ApiResponse

router = APIRouter()

def get_youtube_questions_use_case(llm_service = Depends(get_llm_service)) -> GenerateVideoQuestionsUseCase:
    youtube_adapter = YouTubeTranscriptAdapter()
    return GenerateVideoQuestionsUseCase(youtube_adapter=youtube_adapter, llm_service=llm_service)

@router.post("/youtube-questions", response_model=ApiResponse[List[YouTubeQuestionResponse]], status_code=status.HTTP_200_OK)
async def generate_youtube_questions(
    request: YouTubeQuestionRequest,
    current_user: CurrentUserDep,
    use_case: GenerateVideoQuestionsUseCase = Depends(get_youtube_questions_use_case),
):
    """
    Tạo câu hỏi tự động từ video YouTube (UC-FT-014).
    Yêu cầu:
    - Video không quá 30 phút.
    - Video phải có phụ đề (CC).
    """
    try:
        data = await use_case.execute(url=request.url, question_count=request.question_count)
        return ApiResponse(data=data, message="Tạo câu hỏi từ video YouTube thành công")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Lỗi hệ thống khi tạo câu hỏi từ video.")
