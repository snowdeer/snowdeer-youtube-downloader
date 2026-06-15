from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class DownloadFormat(str, Enum):
    mp4 = "mp4"
    mp3 = "mp3"


class DownloadStatus(str, Enum):
    pending = "pending"
    downloading = "downloading"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class DownloadJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    url: str
    format: DownloadFormat
    status: DownloadStatus = DownloadStatus.pending
    progress_percent: int = Field(default=0, ge=0, le=100)
    file_path: str | None = None
    file_name: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DownloadRequest(BaseModel):
    url: str
    format: DownloadFormat


class DownloadProgress(BaseModel):
    job_id: str
    status: DownloadStatus
    progress_percent: int
    message: str | None = None
