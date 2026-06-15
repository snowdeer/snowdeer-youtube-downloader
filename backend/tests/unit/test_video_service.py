from unittest.mock import AsyncMock, patch

import pytest

from app.models.video import VideoInfo


@pytest.mark.asyncio
async def test_video_service_get_video_info_calls_wrapper():
    mock_info = VideoInfo(
        url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        thumbnail_url="https://example.com/thumb.jpg",
        duration_seconds=120,
        channel="Test Channel",
    )

    with patch("app.services.video_service.get_video_info", new=AsyncMock(return_value=mock_info)):
        from app.services.video_service import VideoService

        service = VideoService()
        result = await service.get_video_info("https://www.youtube.com/watch?v=test123")

    assert result.title == "Test Video"
    assert result.url == "https://www.youtube.com/watch?v=test123"


@pytest.mark.asyncio
async def test_video_service_propagates_value_error():
    with patch(
        "app.services.video_service.get_video_info",
        new=AsyncMock(side_effect=ValueError("유효한 유튜브 URL이 아닙니다")),
    ):
        from app.services.video_service import VideoService

        service = VideoService()
        with pytest.raises(ValueError, match="유효한 유튜브 URL"):
            await service.get_video_info("https://www.google.com")


@pytest.mark.asyncio
async def test_video_service_propagates_lookup_error():
    with patch(
        "app.services.video_service.get_video_info",
        new=AsyncMock(side_effect=LookupError("영상을 찾을 수 없거나")),
    ):
        from app.services.video_service import VideoService

        service = VideoService()
        with pytest.raises(LookupError):
            await service.get_video_info("https://www.youtube.com/watch?v=private")
