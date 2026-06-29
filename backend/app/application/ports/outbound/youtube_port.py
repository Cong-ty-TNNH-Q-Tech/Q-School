from abc import ABC, abstractmethod
from typing import List, Dict

class IYouTubeTranscriptAdapter(ABC):
    @abstractmethod
    async def get_transcript(self, video_id: str) -> List[Dict[str, float | str]]:
        """
        Lấy transcript của video YouTube.
        
        Args:
            video_id: ID của video trên YouTube
            
        Returns:
            Danh sách các dict chứa 'text', 'start', 'duration'
            
        Raises:
            ValueError: Nếu video không có transcript (CC)
        """
        pass
