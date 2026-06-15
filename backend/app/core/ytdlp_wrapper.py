import asyncio
import re
from concurrent.futures import ThreadPoolExecutor

import yt_dlp

from app.models.video import VideoInfo

YOUTUBE_URL_PATTERN = re.compile(
    r"https://(www\.)?youtube\.com/watch\?v=|https://youtu\.be/"
)

_executor = ThreadPoolExecutor(max_workers=2)


def _extract_info_sync(url: str) -> dict:
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)  # type: ignore[return-value]


def _download_sync(url: str, fmt: str, output_dir: str, progress_callback=None) -> str:
    if fmt == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
        }
    else:
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": True,
        }

    if progress_callback:
        ydl_opts["progress_hooks"] = [progress_callback]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)  # type: ignore[arg-type]


async def get_video_info(url: str) -> VideoInfo:
    if not YOUTUBE_URL_PATTERN.match(url):
        raise ValueError("유효한 유튜브 URL이 아닙니다")

    loop = asyncio.get_event_loop()
    try:
        info = await loop.run_in_executor(_executor, _extract_info_sync, url)
    except yt_dlp.utils.DownloadError as e:
        raise LookupError("영상을 찾을 수 없거나 접근이 제한된 영상입니다") from e

    return VideoInfo(
        url=url,
        title=info.get("title", ""),
        thumbnail_url=info.get("thumbnail"),
        duration_seconds=info.get("duration"),
        channel=info.get("uploader") or info.get("channel"),
    )


async def download_video(
    url: str,
    fmt: str,
    output_dir: str,
    progress_callback=None,
) -> str:
    loop = asyncio.get_event_loop()
    try:
        file_path = await loop.run_in_executor(
            _executor, _download_sync, url, fmt, output_dir, progress_callback
        )
    except yt_dlp.utils.DownloadError as e:
        raise RuntimeError(f"다운로드 실패: {e}") from e
    return file_path
