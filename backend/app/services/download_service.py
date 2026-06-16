import os
import re
import threading
from typing import Callable
from urllib.parse import quote

from app.core import ytdlp_wrapper
from app.models.download import DownloadFormat, DownloadJob, DownloadProgress, DownloadStatus

_FORBIDDEN_FILENAME_CHARS = re.compile(r'[/\\:*?"<>|]')


def build_content_disposition(file_name: str) -> str:
    ascii_fallback = _FORBIDDEN_FILENAME_CHARS.sub("_", file_name).encode("ascii", "replace").decode("ascii")
    utf8_encoded = quote(file_name)
    return f'attachment; filename="{ascii_fallback}"; filename*=UTF-8\'\'{utf8_encoded}'


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

    def get_completed_file(self, job_id: str) -> tuple[str, str]:
        job = self._jobs.get(job_id)
        if job is None:
            raise LookupError("해당 다운로드 작업을 찾을 수 없습니다")
        if job.status != DownloadStatus.completed or not job.file_path:
            raise RuntimeError("다운로드가 아직 완료되지 않았습니다")
        if not os.path.isfile(job.file_path):
            raise RuntimeError("다운로드 파일을 찾을 수 없습니다. 만료되었거나 삭제되었을 수 있습니다")
        return job.file_path, job.file_name or os.path.basename(job.file_path)

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
