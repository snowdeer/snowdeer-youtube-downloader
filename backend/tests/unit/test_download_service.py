from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.download import DownloadFormat, DownloadStatus


@pytest.mark.asyncio
async def test_start_download_creates_pending_job():
    from app.services.download_service import DownloadService

    service = DownloadService()

    with patch.object(service, "_run_download", new=AsyncMock()):
        job = await service.start_download(
            "https://www.youtube.com/watch?v=test123",
            DownloadFormat.mp4,
        )

    assert job.status == DownloadStatus.pending
    assert job.url == "https://www.youtube.com/watch?v=test123"
    assert job.format == DownloadFormat.mp4
    assert job.job_id is not None


@pytest.mark.asyncio
async def test_start_download_rejects_concurrent_requests():
    from app.services.download_service import DownloadService
    from app.models.download import DownloadJob, DownloadStatus

    service = DownloadService()
    job = DownloadJob(
        url="https://www.youtube.com/watch?v=test123",
        format=DownloadFormat.mp4,
        status=DownloadStatus.downloading,
    )
    service._jobs[job.job_id] = job

    with pytest.raises(RuntimeError, match="이미 진행 중"):
        await service.start_download(
            "https://www.youtube.com/watch?v=test456",
            DownloadFormat.mp3,
        )


def test_progress_hook_updates_progress_store():
    from app.services.download_service import DownloadService

    service = DownloadService()
    job_id = "test-job-id"
    from app.models.download import DownloadJob
    service._jobs[job_id] = DownloadJob(
        job_id=job_id,
        url="https://www.youtube.com/watch?v=test",
        format=DownloadFormat.mp4,
    )

    hook = service._make_progress_hook(job_id)
    hook({"status": "downloading", "downloaded_bytes": 50, "total_bytes": 100})

    progress = service.get_progress(job_id)
    assert progress is not None
    assert progress.progress_percent == 50
    assert progress.status == DownloadStatus.downloading


def test_get_progress_returns_none_for_unknown_job():
    from app.services.download_service import DownloadService

    service = DownloadService()
    assert service.get_progress("nonexistent-id") is None


@pytest.mark.asyncio
async def test_mp4_format_uses_correct_ytdlp_options():
    from app.services.download_service import DownloadService

    service = DownloadService()

    captured_fmt = []

    async def fake_download(url, fmt, output_dir, progress_callback=None):
        captured_fmt.append(fmt)
        return "/tmp/test.mp4"

    with patch("app.services.download_service.ytdlp_wrapper.download_video", new=fake_download):
        from app.models.download import DownloadJob
        job = DownloadJob(
            url="https://www.youtube.com/watch?v=test",
            format=DownloadFormat.mp4,
            status=DownloadStatus.pending,
        )
        service._jobs[job.job_id] = job
        service._progress_store[job.job_id] = MagicMock()
        await service._run_download(job)

    assert "mp4" in captured_fmt


@pytest.mark.asyncio
async def test_mp3_format_uses_correct_ytdlp_options():
    from app.services.download_service import DownloadService

    service = DownloadService()
    captured_fmt = []

    async def fake_download(url, fmt, output_dir, progress_callback=None):
        captured_fmt.append(fmt)
        return "/tmp/test.mp3"

    with patch("app.services.download_service.ytdlp_wrapper.download_video", new=fake_download):
        from app.models.download import DownloadJob
        job = DownloadJob(
            url="https://www.youtube.com/watch?v=test",
            format=DownloadFormat.mp3,
            status=DownloadStatus.pending,
        )
        service._jobs[job.job_id] = job
        service._progress_store[job.job_id] = MagicMock()
        await service._run_download(job)

    assert "mp3" in captured_fmt


def test_get_completed_file_returns_path_and_name(tmp_path):
    from app.models.download import DownloadJob
    from app.services.download_service import DownloadService

    file_path = tmp_path / "영상 제목.mp4"
    file_path.write_bytes(b"fake video data")

    service = DownloadService()
    job = DownloadJob(
        url="https://www.youtube.com/watch?v=test",
        format=DownloadFormat.mp4,
        status=DownloadStatus.completed,
        file_path=str(file_path),
        file_name="영상 제목.mp4",
    )
    service._jobs[job.job_id] = job

    path, name = service.get_completed_file(job.job_id)

    assert path == str(file_path)
    assert name == "영상 제목.mp4"


def test_get_completed_file_raises_lookup_error_for_unknown_job():
    from app.services.download_service import DownloadService

    service = DownloadService()

    with pytest.raises(LookupError):
        service.get_completed_file("nonexistent-id")


def test_get_completed_file_raises_runtime_error_when_not_completed():
    from app.models.download import DownloadJob
    from app.services.download_service import DownloadService

    service = DownloadService()
    job = DownloadJob(
        url="https://www.youtube.com/watch?v=test",
        format=DownloadFormat.mp4,
        status=DownloadStatus.downloading,
    )
    service._jobs[job.job_id] = job

    with pytest.raises(RuntimeError):
        service.get_completed_file(job.job_id)


def test_get_completed_file_raises_runtime_error_when_file_missing(tmp_path):
    from app.models.download import DownloadJob
    from app.services.download_service import DownloadService

    missing_path = tmp_path / "deleted.mp4"

    service = DownloadService()
    job = DownloadJob(
        url="https://www.youtube.com/watch?v=test",
        format=DownloadFormat.mp4,
        status=DownloadStatus.completed,
        file_path=str(missing_path),
        file_name="deleted.mp4",
    )
    service._jobs[job.job_id] = job

    with pytest.raises(RuntimeError):
        service.get_completed_file(job.job_id)


def test_build_content_disposition_includes_ascii_fallback_and_utf8_filename():
    from app.services.download_service import build_content_disposition

    header = build_content_disposition("테스트 영상!.mp4")

    assert header.startswith("attachment;")
    assert "filename=" in header
    assert "filename*=UTF-8''" in header


def test_build_content_disposition_sanitizes_forbidden_characters():
    from app.services.download_service import build_content_disposition

    header = build_content_disposition('a/b\\c:d*e?f"g<h>i|j.mp4')

    ascii_part = header.split("filename=")[1].split(";")[0].strip('"')
    for forbidden in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        assert forbidden not in ascii_part
