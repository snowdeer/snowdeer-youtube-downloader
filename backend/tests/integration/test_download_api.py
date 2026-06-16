from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.download import DownloadFormat, DownloadJob, DownloadProgress, DownloadStatus


@pytest.mark.asyncio
async def test_start_download_returns_202_with_job_id(client):
    mock_job = DownloadJob(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        format=DownloadFormat.mp4,
        status=DownloadStatus.pending,
    )

    with patch(
        "app.api.routes.download.download_service.start_download",
        new=AsyncMock(return_value=mock_job),
    ):
        response = await client.post(
            "/api/download/start",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "format": "mp4",
            },
        )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_start_download_returns_409_when_concurrent(client):
    with patch(
        "app.api.routes.download.download_service.start_download",
        new=AsyncMock(side_effect=RuntimeError("이미 진행 중인 다운로드가 있습니다. 완료 후 다시 시도하세요.")),
    ):
        response = await client.post(
            "/api/download/start",
            json={
                "url": "https://www.youtube.com/watch?v=test456",
                "format": "mp3",
            },
        )

    assert response.status_code == 409
    assert "이미 진행 중" in response.json()["detail"]


@pytest.mark.asyncio
async def test_start_download_returns_422_for_invalid_format(client):
    response = await client.post(
        "/api/download/start",
        json={
            "url": "https://www.youtube.com/watch?v=test",
            "format": "avi",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_download_status_returns_job(client):
    mock_job = DownloadJob(
        job_id="test-job-id",
        url="https://www.youtube.com/watch?v=test",
        format=DownloadFormat.mp4,
        status=DownloadStatus.downloading,
        progress_percent=50,
    )

    with patch.object(
        __import__("app.services.download_service", fromlist=["download_service"]).download_service,
        "get_job",
        return_value=mock_job,
    ):
        response = await client.get("/api/download/test-job-id/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "downloading"
    assert data["progress_percent"] == 50


@pytest.mark.asyncio
async def test_get_download_status_returns_404_for_unknown_job(client):
    with patch(
        "app.api.routes.download.download_service.get_job",
        return_value=None,
    ):
        response = await client.get("/api/download/nonexistent-id/status")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_file_returns_200_with_mp4_content(client, tmp_path):
    file_path = tmp_path / "테스트 영상.mp4"
    file_path.write_bytes(b"fake mp4 bytes")

    with patch(
        "app.api.routes.download.download_service.get_completed_file",
        return_value=(str(file_path), "테스트 영상.mp4"),
    ):
        response = await client.get("/api/download/test-job-id/file")

    assert response.status_code == 200
    assert response.headers["content-type"] == "video/mp4"
    assert response.content == b"fake mp4 bytes"
    assert "Content-Disposition" in response.headers
    assert "filename*=UTF-8''" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_download_file_returns_200_with_mp3_content(client, tmp_path):
    file_path = tmp_path / "테스트 음원.mp3"
    file_path.write_bytes(b"fake mp3 bytes")

    with patch(
        "app.api.routes.download.download_service.get_completed_file",
        return_value=(str(file_path), "테스트 음원.mp3"),
    ):
        response = await client.get("/api/download/test-job-id/file")

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"


@pytest.mark.asyncio
async def test_download_file_returns_404_for_unknown_job(client):
    with patch(
        "app.api.routes.download.download_service.get_completed_file",
        side_effect=LookupError("해당 다운로드 작업을 찾을 수 없습니다"),
    ):
        response = await client.get("/api/download/nonexistent-id/file")

    assert response.status_code == 404
    assert "찾을 수 없습니다" in response.json()["detail"]


@pytest.mark.asyncio
async def test_download_file_returns_409_when_not_completed(client):
    with patch(
        "app.api.routes.download.download_service.get_completed_file",
        side_effect=RuntimeError("다운로드가 아직 완료되지 않았습니다"),
    ):
        response = await client.get("/api/download/test-job-id/file")

    assert response.status_code == 409
    assert "완료되지 않았습니다" in response.json()["detail"]


@pytest.mark.asyncio
async def test_download_file_content_length_matches_file_size(client, tmp_path):
    file_path = tmp_path / "큰 파일.mp4"
    file_path.write_bytes(b"x" * 12345)

    with patch(
        "app.api.routes.download.download_service.get_completed_file",
        return_value=(str(file_path), "큰 파일.mp4"),
    ):
        response = await client.get("/api/download/test-job-id/file")

    assert response.status_code == 200
    assert response.headers["content-length"] == "12345"
