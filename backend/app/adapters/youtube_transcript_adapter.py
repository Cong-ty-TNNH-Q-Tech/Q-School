import asyncio
import os
import tempfile
import logging
import yt_dlp
import whisper
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from app.application.ports.outbound.youtube_port import IYouTubeTranscriptAdapter

logger = logging.getLogger(__name__)

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        logger.info("Đang load Whisper model vào RAM (chỉ chạy 1 lần)...")
        _whisper_model = whisper.load_model("base")
    return _whisper_model

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
            logger.warning(f"Video {video_id} không có phụ đề. Khởi chạy fallback yt-dlp + Whisper...")
            return await self._fallback_transcribe(video_id)
        except Exception as e:
            raise ValueError(f"Không thể tải phụ đề: {str(e)}") from e

    async def _fallback_transcribe(self, video_id: str) -> List[Dict[str, float | str]]:
        def _sync_transcribe():
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                audio_path = os.path.join(tmp_dir, f"{video_id}.m4a")
                
                ydl_opts = {
                    'format': 'm4a/bestaudio/best',
                    'outtmpl': audio_path,
                    'quiet': True,
                    'no_warnings': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'm4a',
                    }]
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        logger.info(f"Đang tải audio từ {url}...")
                        ydl.download([url])
                except Exception as e:
                    logger.error(f"Lỗi tải audio bằng yt-dlp: {e}")
                    raise ValueError("Không thể tải video để trích xuất âm thanh.") from e
                
                if not os.path.exists(audio_path):
                    raise ValueError("Không thể trích xuất file audio từ video này.")
                
                logger.info(f"Đang chạy Whisper để tạo phụ đề cho {video_id}...")
                try:
                    # Sử dụng model 'base' được cache
                    model = get_whisper_model()
                    result = model.transcribe(audio_path)
                except Exception as e:
                    logger.error(f"Lỗi khi chạy Whisper: {e}")
                    raise ValueError("Có lỗi xảy ra trong quá trình nhận diện giọng nói.") from e
                
                transcript_data = []
                for segment in result.get("segments", []):
                    transcript_data.append({
                        "start": segment["start"],
                        "duration": segment["end"] - segment["start"],
                        "text": segment["text"].strip()
                    })
                    
                if not transcript_data:
                    raise ValueError("Video này không có giọng nói hoặc không nhận diện được.")
                    
                return transcript_data
                
        return await asyncio.to_thread(_sync_transcribe)
