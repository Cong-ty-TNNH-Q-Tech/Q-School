import asyncio
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from app.application.ports.outbound.youtube_port import IYouTubeTranscriptAdapter

class YouTubeTranscriptAdapter(IYouTubeTranscriptAdapter):
    async def get_transcript(self, video_id: str) -> List[Dict[str, float | str]]:
        try:
            # Chạy trong threadpool để không block event loop
            return await asyncio.to_thread(
                YouTubeTranscriptApi.get_transcript,
                video_id,
                languages=['vi', 'en']
            )
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise ValueError("Video không có phụ đề (CC).") from e
        except Exception as e:
            raise ValueError(f"Không thể tải phụ đề: {str(e)}") from e
