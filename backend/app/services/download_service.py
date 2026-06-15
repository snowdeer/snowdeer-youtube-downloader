import os
import threading
from typing import Callable

from app.core import ytdlp_wrapper
from app.models.download import DownloadFormat, DownloadJob, DownloadProgress, DownloadStatus


class DownloadService:
    def __init__(self):
        self._jobs: dict[str, DownloadJob] = {}
        self._progress_store: dict[str, DownloadProgress] = {}
        self._lock = threading.Lock()
        self._download_dir = os.getenv("DOWNLOAD_DIR", "./downloads")

    def _has_active_job(self) -> bool:
        with self._lock:
            return any(
                j.status in (DownloadStatus.pending, DownloadStatus.downloading, DownloadStatus.processing)
                for j in self._jobs.values()
            )

    def get_job(self, job_id: str) -> DownloadJob | None:
        return self._jobs.get(job_id)

    def get_progress(self, job_id: str) -> DownloadProgress | None:
        return self._progress_store.get(job_id)

    def _update_progress(self, job_id: str, status: DownloadStatus, percent: int, message: str | None = None):
        with self._lock:
            self._progress_store[job_id] = DownloadProgress(
                job_id=job_id,
                status=status,
                progress_percent=percent,
                message=message,
            )
            if job_id in self._jobs:
                self._jobs[job_id].status = status
                self._jobs[job_id].progress_percent = percent

    def _make_progress_hook(self, job_id: str) -> Callable:
        def hook(d: dict):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
                downloaded = d.get("downloaded_bytes", 0)
                percent = int(downloaded / total * 100)
                self._update_progress(job_id, DownloadStatus.downloading, percent, "다운로드 중...")
            elif d["status"] == "finished":
                self._update_progress(job_id, DownloadStatus.processing, 95, "변환 중...")
        return hook

    async def start_download(self, url: str, fmt: DownloadFormat) -> DownloadJob:
        if self._has_active_job():
            raise RuntimeError("이미 진행 중인 다운로드가 있습니다. 완료 후 다시 시도하세요.")

        job = DownloadJob(url=url, format=fmt)
        with self._lock:
            self._jobs[job.job_id] = job

        self._update_progress(job.job_id, DownloadStatus.pending, 0, "대기 중...")

        import asyncio
        asyncio.create_task(self._run_download(job))
        return job

    async def _run_download(self, job: DownloadJob):
        job_dir = os.path.join(self._download_dir, job.job_id)
        os.makedirs(job_dir, exist_ok=True)

        self._update_progress(job.job_id, DownloadStatus.downloading, 0, "다운로드 시작...")
        try:
            hook = self._make_progress_hook(job.job_id)
            file_path = await ytdlp_wrapper.download_video(
                url=job.url,
                fmt=job.format.value,
                output_dir=job_dir,
                progress_callback=hook,
            )
            file_name = os.path.basename(file_path)
            with self._lock:
                self._jobs[job.job_id].file_path = file_path
                self._jobs[job.job_id].file_name = file_name
            self._update_progress(job.job_id, DownloadStatus.completed, 100, "완료")
        except Exception as e:
            with self._lock:
                self._jobs[job.job_id].error_message = str(e)
            self._update_progress(job.job_id, DownloadStatus.failed, 0, str(e))


download_service = DownloadService()
