import re

from pydantic import BaseModel, field_validator

YOUTUBE_URL_PATTERN = re.compile(
    r"https://(www\.)?youtube\.com/watch\?v=|https://youtu\.be/"
)


class VideoInfo(BaseModel):
    url: str
    title: str
    thumbnail_url: str | None = None
    duration_seconds: int | None = None
    channel: str | None = None

    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        if not YOUTUBE_URL_PATTERN.match(v):
            raise ValueError("유효한 유튜브 URL이 아닙니다")
        return v


class VideoInfoRequest(BaseModel):
    url: str
