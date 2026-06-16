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


def test_download_sync_uses_postprocessed_filepath_when_available(tmp_path):
    from app.core import ytdlp_wrapper

    final_path = str(tmp_path / "song.mp3")
    stale_path = str(tmp_path / "song.webm")
    mock_info = {"filepath": final_path, "ext": "mp3"}

    class FakeYDL:
        def __init__(self, opts):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def extract_info(self, url, download=True):
            return mock_info

        def prepare_filename(self, info):
            return stale_path

    with patch("app.core.ytdlp_wrapper.yt_dlp.YoutubeDL", FakeYDL):
        result = ytdlp_wrapper._download_sync("https://www.youtube.com/watch?v=test", "mp3", str(tmp_path))

    assert result == final_path


def test_download_sync_falls_back_to_prepare_filename_when_filepath_missing(tmp_path):
    from app.core import ytdlp_wrapper

    expected_path = str(tmp_path / "video.mp4")
    mock_info = {"ext": "mp4"}

    class FakeYDL:
        def __init__(self, opts):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def extract_info(self, url, download=True):
            return mock_info

        def prepare_filename(self, info):
            return expected_path

    with patch("app.core.ytdlp_wrapper.yt_dlp.YoutubeDL", FakeYDL):
        result = ytdlp_wrapper._download_sync("https://www.youtube.com/watch?v=test", "mp4", str(tmp_path))

    assert result == expected_path


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
