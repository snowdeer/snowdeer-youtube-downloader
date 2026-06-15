import asyncio

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.models.download import DownloadJob, DownloadRequest, DownloadStatus
from app.services.download_service import download_service

router = APIRouter()


@router.post("/start", response_model=DownloadJob, status_code=202)
async def start_download(request: DownloadRequest):
    try:
        job = await download_service.start_download(request.url, request.format)
        return job
    except RuntimeError as e:
        msg = str(e)
        if "이미 진행 중" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=422, detail=msg)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{job_id}/status", response_model=DownloadJob)
async def get_download_status(job_id: str):
    job = download_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="해당 다운로드 작업을 찾을 수 없습니다")
    return job


@router.get("/{job_id}/progress")
async def get_download_progress(job_id: str):
    if not download_service.get_job(job_id):
        raise HTTPException(status_code=404, detail="해당 다운로드 작업을 찾을 수 없습니다")

    async def event_generator():
        while True:
            progress = download_service.get_progress(job_id)
            if progress:
                yield {"data": progress.model_dump_json()}
                if progress.status in (DownloadStatus.completed, DownloadStatus.failed):
                    break
            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())
