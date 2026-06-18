import asyncio
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from sse_starlette.sse import EventSourceResponse

from app.models.download import DownloadJob, DownloadRequest, DownloadStatus
from app.services.download_service import build_content_disposition, download_service

router = APIRouter()

_CONTENT_TYPE_BY_EXTENSION = {
    ".mp4": "video/mp4",
    ".mp3": "audio/mpeg",
}


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


def _file_response_headers(job_id: str) -> tuple[str, str, str]:
    """파일 경로, 파일명, Content-Type 을 반환한다. 오류 시 HTTPException 을 발생시킨다."""
    try:
        file_path, file_name = download_service.get_completed_file(job_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        msg = str(e)
        status_code = 404 if "찾을 수 없습니다" in msg else 409
        raise HTTPException(status_code=status_code, detail=msg)
    ext = os.path.splitext(file_name)[1].lower()
    media_type = _CONTENT_TYPE_BY_EXTENSION.get(ext, "application/octet-stream")
    return file_path, file_name, media_type


@router.head("/{job_id}/file")
async def head_download_file(job_id: str):
    _, file_name, media_type = _file_response_headers(job_id)
    return Response(
        headers={"Content-Disposition": build_content_disposition(file_name)},
        media_type=media_type,
    )


@router.get("/{job_id}/file")
async def download_file(job_id: str):
    file_path, file_name, media_type = _file_response_headers(job_id)
    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers={"Content-Disposition": build_content_disposition(file_name)},
    )
