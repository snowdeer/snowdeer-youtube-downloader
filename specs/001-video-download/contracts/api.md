# API Contract: 유튜브 동영상 다운로더

**Date**: 2026-06-15
**Base URL**: `http://localhost:7990/api`
**Content-Type**: `application/json` (SSE 엔드포인트 제외)

---

## 엔드포인트 목록

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/video/info` | 유튜브 URL로 영상 정보 조회 |
| POST | `/download/start` | 다운로드 작업 시작 |
| GET | `/download/{job_id}/progress` | SSE 진행률 스트림 |
| GET | `/download/{job_id}/status` | 현재 다운로드 상태 조회 |

---

## POST `/video/info`

유튜브 URL에서 영상 메타데이터를 조회한다.

### Request

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

### Response 200 OK

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "duration_seconds": 212,
  "channel": "Rick Astley"
}
```

### Response 422 Unprocessable Entity (유효하지 않은 URL)

```json
{
  "detail": "유효한 유튜브 URL이 아닙니다"
}
```

### Response 404 Not Found (영상 없음 / 비공개)

```json
{
  "detail": "영상을 찾을 수 없거나 접근이 제한된 영상입니다"
}
```

---

## POST `/download/start`

다운로드 작업을 생성하고 백그라운드에서 다운로드를 시작한다.

### Request

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp4"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `url` | string | ✅ | 유튜브 영상 URL |
| `format` | string | ✅ | `"mp4"` 또는 `"mp3"` |

### Response 202 Accepted

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp4",
  "status": "pending",
  "progress_percent": 0,
  "created_at": "2026-06-15T10:00:00Z"
}
```

### Response 409 Conflict (이미 진행 중인 다운로드 있음)

```json
{
  "detail": "이미 진행 중인 다운로드가 있습니다. 완료 후 다시 시도하세요."
}
```

### Response 422 Unprocessable Entity

```json
{
  "detail": "유효한 유튜브 URL이 아닙니다"
}
```

---

## GET `/download/{job_id}/progress`

SSE(Server-Sent Events) 스트림으로 실시간 진행률을 수신한다.

### Headers

```
Accept: text/event-stream
Cache-Control: no-cache
```

### SSE Event Stream 형식

각 이벤트는 아래 JSON 페이로드를 담은 `data:` 라인으로 전송된다.

**진행 중 이벤트**:
```
data: {"job_id": "550e8400-...", "status": "downloading", "progress_percent": 45, "message": "다운로드 중..."}

data: {"job_id": "550e8400-...", "status": "processing", "progress_percent": 90, "message": "변환 중..."}
```

**완료 이벤트**:
```
data: {"job_id": "550e8400-...", "status": "completed", "progress_percent": 100, "message": "완료"}
```

**실패 이벤트**:
```
data: {"job_id": "550e8400-...", "status": "failed", "progress_percent": 0, "message": "네트워크 오류가 발생했습니다"}
```

- `status`가 `completed` 또는 `failed`이면 스트림이 종료된다.
- 갱신 주기: 최대 1초.

### Response 404 (job_id 없음)

```
HTTP/1.1 404 Not Found
Content-Type: application/json

{"detail": "해당 다운로드 작업을 찾을 수 없습니다"}
```

---

## GET `/download/{job_id}/status`

현재 다운로드 작업 상태를 단일 응답으로 조회한다 (폴링용).

### Response 200 OK

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp4",
  "status": "completed",
  "progress_percent": 100,
  "file_name": "Rick Astley - Never Gonna Give You Up.mp4",
  "error_message": null,
  "created_at": "2026-06-15T10:00:00Z"
}
```

### Response 404

```json
{
  "detail": "해당 다운로드 작업을 찾을 수 없습니다"
}
```

---

## 오류 응답 공통 형식

```json
{
  "detail": "오류 메시지 (한국어)"
}
```

## CORS 설정

개발 환경에서 프론트엔드 (`http://localhost:5173`) 에서의 요청을 허용한다.
