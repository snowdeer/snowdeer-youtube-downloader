from unittest.mock import AsyncMock, patch

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


def test_resolve_single_video_returns_video_directly():
    from app.core.ytdlp_wrapper import _resolve_single_video

    video_info = {"_type": "video", "title": "Test", "duration": 120}
    assert _resolve_single_video(video_info) is video_info


def test_resolve_single_video_extracts_first_entry_from_playlist():
    from app.core.ytdlp_wrapper import _resolve_single_video

    first_entry = {"title": "First Video", "duration": 100}
    playlist_info = {
        "_type": "playlist",
        "entries": [first_entry, {"title": "Second Video"}],
    }
    result = _resolve_single_video(playlist_info)
    assert result["title"] == "First Video"


def test_resolve_single_video_raises_for_empty_playlist():
    from app.core.ytdlp_wrapper import _resolve_single_video

    with pytest.raises(LookupError, match="플레이리스트에서 영상을 찾을 수 없습니다"):
        _resolve_single_video({"_type": "playlist", "entries": []})


@pytest.mark.asyncio
async def test_get_video_info_handles_url_with_list_param():
    """list= 파라미터가 포함된 URL도 단일 영상 정보를 반환해야 한다."""
    mock_info = {
        "title": "Radio Video",
        "thumbnail": "https://example.com/thumb.jpg",
        "duration": 200,
        "uploader": "Some Channel",
    }

    with patch("app.core.ytdlp_wrapper.asyncio.get_event_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(return_value=mock_info)

        from app.core.ytdlp_wrapper import get_video_info

        result = await get_video_info(
            "https://www.youtube.com/watch?v=eKtSbXHaqLM&list=RDeKtSbXHaqLM&start_radio=1"
        )

    assert result.title == "Radio Video"
    assert result.duration_seconds == 200
