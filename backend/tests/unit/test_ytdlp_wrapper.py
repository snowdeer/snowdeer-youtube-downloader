from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.video import VideoInfo


@pytest.mark.asyncio
async def test_get_video_info_returns_video_info_for_valid_url():
    mock_info = {
        "title": "Test Video",
        "thumbnail": "https://example.com/thumb.jpg",
        "duration": 120,
        "uploader": "Test Channel",
        "webpage_url": "https://www.youtube.com/watch?v=test123",
    }

    with patch("app.core.ytdlp_wrapper.asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=mock_info)

        from app.core.ytdlp_wrapper import get_video_info

        result = await get_video_info("https://www.youtube.com/watch?v=test123")

    assert isinstance(result, VideoInfo)
    assert result.title == "Test Video"
    assert result.thumbnail_url == "https://example.com/thumb.jpg"
    assert result.duration_seconds == 120
    assert result.channel == "Test Channel"


@pytest.mark.asyncio
async def test_get_video_info_raises_for_invalid_url():
    from app.core.ytdlp_wrapper import get_video_info

    with pytest.raises(ValueError, match="유효한 유튜브 URL"):
        await get_video_info("https://www.google.com")


@pytest.mark.asyncio
async def test_get_video_info_raises_for_unavailable_video():
    import yt_dlp

    with patch("app.core.ytdlp_wrapper.asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(
            side_effect=yt_dlp.utils.DownloadError("Video unavailable")
        )

        from app.core.ytdlp_wrapper import get_video_info

        with pytest.raises(LookupError, match="영상을 찾을 수 없거나"):
            await get_video_info("https://www.youtube.com/watch?v=unavailable")
