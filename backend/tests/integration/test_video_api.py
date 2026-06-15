from unittest.mock import AsyncMock, patch

import pytest

from app.models.video import VideoInfo


@pytest.mark.asyncio
async def test_post_video_info_returns_200_for_valid_url(client):
    mock_info = VideoInfo(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        title="Rick Astley - Never Gonna Give You Up",
        thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        duration_seconds=212,
        channel="Rick Astley",
    )

    with patch(
        "app.api.routes.video.video_service.get_video_info",
        new=AsyncMock(return_value=mock_info),
    ):
        response = await client.post(
            "/api/video/info",
            json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Rick Astley - Never Gonna Give You Up"
    assert data["duration_seconds"] == 212


@pytest.mark.asyncio
async def test_post_video_info_returns_422_for_invalid_url(client):
    with patch(
        "app.api.routes.video.video_service.get_video_info",
        new=AsyncMock(side_effect=ValueError("유효한 유튜브 URL이 아닙니다")),
    ):
        response = await client.post(
            "/api/video/info",
            json={"url": "https://www.google.com"},
        )

    assert response.status_code == 422
    assert "유효한 유튜브 URL" in response.json()["detail"]


@pytest.mark.asyncio
async def test_post_video_info_returns_404_for_unavailable_video(client):
    with patch(
        "app.api.routes.video.video_service.get_video_info",
        new=AsyncMock(side_effect=LookupError("영상을 찾을 수 없거나 접근이 제한된 영상입니다")),
    ):
        response = await client.post(
            "/api/video/info",
            json={"url": "https://www.youtube.com/watch?v=private123"},
        )

    assert response.status_code == 404
    assert "찾을 수 없거나" in response.json()["detail"]
