import re
import json
import logging
from typing import List
from app.application.ports.outbound.youtube_port import IYouTubeTranscriptAdapter
from app.application.ports.outbound.llm_service import ILLMService
from app.entrypoints.api_v1.schemas.youtube import YouTubeQuestionResponse

logger = logging.getLogger(__name__)

class GenerateVideoQuestionsUseCase:
    def __init__(self, youtube_adapter: IYouTubeTranscriptAdapter, llm_service: ILLMService):
        self.youtube_adapter = youtube_adapter
        self.llm_service = llm_service

    def _extract_video_id(self, url: str) -> str:
        # Hỗ trợ cả youtu.be và youtube.com
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, url)
        if not match:
            raise ValueError("URL YouTube không hợp lệ.")
        return match.group(1)

    async def execute(self, url: str, question_count: int) -> List[YouTubeQuestionResponse]:
        video_id = self._extract_video_id(url)
        
        # 1. Tải transcript
        transcript = await self.youtube_adapter.get_transcript(video_id)
        
        if not transcript:
            raise ValueError("Video không có phụ đề (CC).")
            
        # 2. Check duration (Validation: Video không quá 30 phút)
        last_item = transcript[-1]
        total_duration = last_item.get('start', 0) + last_item.get('duration', 0)
        if total_duration > 1800: # 30 phút = 1800 giây
            raise ValueError("Video quá dài. Vui lòng chọn video dưới 30 phút.")
                
        # 3. Chuẩn bị dữ liệu cho AI
        transcript_text = "\n".join([f"[{int(item['start'])}s] {item['text']}" for item in transcript])
        
        # 4. Gọi LLM
        prompt = f"""Dựa vào nội dung phụ đề video dưới đây, hãy tạo {question_count} câu hỏi trắc nghiệm (mỗi câu 4 đáp án).
Yêu cầu BẮT BUỘC:
1. Mỗi câu hỏi phải có timestamp (thời gian tính bằng giây) thể hiện vị trí trong video mà có câu trả lời.
2. Trả lời bằng định dạng JSON HỢP LỆ theo đúng schema sau, TUYỆT ĐỐI KHÔNG giải thích gì thêm:
[
  {{
    "question_text": "Nội dung câu hỏi?",
    "timestamp": 120,
    "answers": [
      {{"text": "Lựa chọn đúng", "is_correct": true}},
      {{"text": "Lựa chọn sai", "is_correct": false}},
      {{"text": "Lựa chọn sai", "is_correct": false}},
      {{"text": "Lựa chọn sai", "is_correct": false}}
    ]
  }}
]

Phụ đề:
{transcript_text}
"""
        
        logger.info(f"Đang gọi AI để tạo {question_count} câu hỏi từ video {video_id}")
        ai_response = await self.llm_service.generate(prompt=prompt, temperature=0.3)
        
        # 5. Parse JSON
        try:
            # Clean markdown code blocks if any
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0]
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].split("```")[0]
            else:
                json_str = ai_response
                
            data = json.loads(json_str.strip())
            return [YouTubeQuestionResponse(**item) for item in data]
        except Exception as e:
            logger.error(f"Lỗi parse JSON từ AI: {ai_response}")
            raise ValueError("Không thể tạo câu hỏi từ video này do lỗi AI format.") from e
