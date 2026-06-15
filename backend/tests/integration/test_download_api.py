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
