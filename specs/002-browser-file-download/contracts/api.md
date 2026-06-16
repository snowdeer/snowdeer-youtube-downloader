# API Contract: 브라우저를 통한 다운로드 파일 전달

**Date**: 2026-06-16
**Base URL**: `http://localhost:7990/api`
**관련 문서**: [001 API 계약](../../001-video-download/contracts/api.md) (본 기능은 아래 엔드포인트 1개를 추가한다)

---

## 엔드포인트 목록 (신규)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/download/{job_id}/file` | 완료된 다운로드 작업의 파일을 브라우저로 전달 |

---

## GET `/download/{job_id}/file`

완료된 다운로드 작업의 결과 파일을 스트리밍 응답으로 전달한다. 브라우저는 이 응답을 받아 사용자의 로컬 PC에 파일을 저장한다.

### Path Parameters

| 필드 | 타입 | 설명 |
|------|------|------|
| `job_id` | string (UUID) | 다운로드 작업 식별자 |

### Response 200 OK

```
HTTP/1.1 200 OK
Content-Type: video/mp4   # format=mp4인 경우. format=mp3인 경우 audio/mpeg
Content-Length: <파일 크기 바이트>
Content-Disposition: attachment; filename="Rick_Astley_-_Never_Gonna_Give_You_Up.mp4"; filename*=UTF-8''Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up.mp4

<binary file stream>
```

| 헤더 | 설명 |
|------|------|
| `Content-Type` | `format`이 `mp4`이면 `video/mp4`, `mp3`이면 `audio/mpeg` |
| `Content-Disposition` | `attachment`로 강제 다운로드 처리. `filename`은 ASCII-safe 대체값, `filename*`은 UTF-8 원본 제목 기반 값 (RFC 5987) |
| `Content-Length` | 파일 전체 크기 (브라우저 다운로드 진행률 표시용) |

### Response 404 Not Found (작업 없음 또는 파일 없음/만료)

```json
{
  "detail": "해당 다운로드 작업을 찾을 수 없습니다"
}
```

```json
{
  "detail": "다운로드 파일을 찾을 수 없습니다. 만료되었거나 삭제되었을 수 있습니다"
}
```

### Response 409 Conflict (아직 완료되지 않은 작업)

```json
{
  "detail": "다운로드가 아직 완료되지 않았습니다"
}
```

---

## 오류 응답 공통 형식

001과 동일하게 모든 오류는 다음 형식을 따른다.

```json
{
  "detail": "오류 메시지 (한국어)"
}
```

## CORS 설정

001과 동일하게 개발 환경에서 프론트엔드(`http://localhost:5173`)의 요청을 허용한다. 파일 다운로드는 동일 출처 정책상 `<a href>` 직접 이동 방식이므로 별도 CORS 이슈는 없으나, 기존 CORS 설정을 그대로 유지한다.
