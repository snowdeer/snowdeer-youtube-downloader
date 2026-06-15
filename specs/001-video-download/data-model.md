# Data Model: 유튜브 동영상 다운로더

**Date**: 2026-06-15
**Feature**: specs/001-video-download/spec.md

## 엔티티 정의

### VideoInfo (영상 정보)

유튜브 URL에서 조회한 영상 메타데이터. 다운로드 시작 전 사용자에게 표시된다.

| 필드 | 타입 | 설명 | 제약 |
|------|------|------|------|
| `url` | string | 원본 유튜브 URL | 필수, 유튜브 URL 패턴 일치 |
| `title` | string | 영상 제목 | 필수, 1~200자 |
| `thumbnail_url` | string | 썸네일 이미지 URL | 선택 |
| `duration_seconds` | integer | 재생 시간(초) | 선택, 0 이상 |
| `channel` | string | 채널명 | 선택 |

**유효성 규칙**:
- `url`은 `https://www.youtube.com/watch?v=` 또는 `https://youtu.be/` 패턴 일치 필수.
- `title`은 빈 문자열 불가.

---

### DownloadFormat (다운로드 형식)

```
enum DownloadFormat:
  mp4  # 동영상 (최고 화질)
  mp3  # 음원 추출 (192kbps)
```

---

### DownloadStatus (다운로드 상태)

```
enum DownloadStatus:
  pending     # 대기 중 (작업 생성됨)
  downloading # 다운로드 진행 중
  processing  # 후처리 중 (mp3 변환 등)
  completed   # 완료
  failed      # 실패
```

**상태 전이**:

```
pending → downloading → processing → completed
                    ↘                ↗
                      → failed
```

---

### DownloadJob (다운로드 작업)

단일 다운로드 요청 및 상태를 나타내는 핵심 엔티티.

| 필드 | 타입 | 설명 | 제약 |
|------|------|------|------|
| `job_id` | string (UUID4) | 작업 고유 식별자 | 필수, UUID4 형식 |
| `url` | string | 다운로드 대상 URL | 필수 |
| `format` | DownloadFormat | 저장 형식 | 필수, mp4 또는 mp3 |
| `status` | DownloadStatus | 현재 상태 | 필수, 기본값: pending |
| `progress_percent` | integer | 진행률 | 0~100, 기본값: 0 |
| `file_path` | string | 저장된 파일 경로 | 완료 후 설정 |
| `file_name` | string | 저장된 파일명 | 완료 후 설정 |
| `error_message` | string | 실패 시 오류 메시지 | 실패 시 설정 |
| `created_at` | datetime | 작업 생성 시각 | 자동 설정 |

**유효성 규칙**:
- `progress_percent`는 0 이상 100 이하.
- `status`가 `completed`이면 `file_path`와 `file_name` 필수.
- `status`가 `failed`이면 `error_message` 필수.
- v1에서는 동시에 활성화된 `DownloadJob` 최대 1개.

---

## 타입 정의 (TypeScript — 프론트엔드)

```typescript
// src/types/index.ts

export type DownloadFormat = 'mp4' | 'mp3';

export type DownloadStatus =
  | 'pending'
  | 'downloading'
  | 'processing'
  | 'completed'
  | 'failed';

export interface VideoInfo {
  url: string;
  title: string;
  thumbnail_url?: string;
  duration_seconds?: number;
  channel?: string;
}

export interface DownloadJob {
  job_id: string;
  url: string;
  format: DownloadFormat;
  status: DownloadStatus;
  progress_percent: number;
  file_name?: string;
  error_message?: string;
  created_at: string;
}

export interface DownloadProgress {
  job_id: string;
  status: DownloadStatus;
  progress_percent: number;
  message?: string;
}
```

---

## Pydantic 모델 (Python — 백엔드)

```python
# app/models/video.py
from pydantic import BaseModel, HttpUrl, field_validator

class VideoInfo(BaseModel):
    url: str
    title: str
    thumbnail_url: str | None = None
    duration_seconds: int | None = None
    channel: str | None = None

    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        import re
        pattern = r'https://(www\.)?youtube\.com/watch\?v=|https://youtu\.be/'
        if not re.match(pattern, v):
            raise ValueError('유효한 유튜브 URL이 아닙니다')
        return v

# app/models/download.py
from enum import Enum
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field

class DownloadFormat(str, Enum):
    mp4 = 'mp4'
    mp3 = 'mp3'

class DownloadStatus(str, Enum):
    pending = 'pending'
    downloading = 'downloading'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'

class DownloadJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    url: str
    format: DownloadFormat
    status: DownloadStatus = DownloadStatus.pending
    progress_percent: int = Field(default=0, ge=0, le=100)
    file_path: str | None = None
    file_name: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DownloadProgress(BaseModel):
    job_id: str
    status: DownloadStatus
    progress_percent: int
    message: str | None = None
```
