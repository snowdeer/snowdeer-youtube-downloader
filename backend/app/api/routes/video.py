from fastapi import APIRouter, HTTPException

from app.models.video import VideoInfo, VideoInfoRequest
from app.services.video_service import video_service

router = APIRouter()


@router.post("/info", response_model=VideoInfo)
async def get_video_info(request: VideoInfoRequest):
    try:
        return await video_service.get_video_info(request.url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
