from app.core.ytdlp_wrapper import get_video_info
from app.models.video import VideoInfo


class VideoService:
    async def get_video_info(self, url: str) -> VideoInfo:
        return await get_video_info(url)


video_service = VideoService()
