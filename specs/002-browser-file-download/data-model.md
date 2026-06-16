# Data Model: 브라우저를 통한 다운로드 파일 전달

**Date**: 2026-06-16
**Feature**: [spec.md](./spec.md)

이 기능은 새로운 영속 엔티티를 추가하지 않는다. 001에서 정의된 `DownloadJob`을 그대로 사용하며, 요청 단위의 비영속 개념인 `FileDeliveryRequest`만 논리적으로 도입한다(별도 저장소 없음, 요청-응답 처리 흐름 안에서만 존재).

## DownloadJob (기존, 001 정의 — 변경 없음)

| 필드 | 타입 | 설명 |
|------|------|------|
| `job_id` | string (UUID) | 다운로드 작업 식별자. 본 기능에서 파일 접근 토큰 역할도 겸함 |
| `url` | string | 원본 유튜브 URL |
| `format` | enum (`mp4`, `mp3`) | 다운로드 형식. 파일 전달 시 `Content-Type` 결정에 사용 |
| `status` | enum (`pending`, `downloading`, `processing`, `completed`, `failed`) | `completed`일 때만 파일 전달 허용 |
| `progress_percent` | int (0-100) | 본 기능에서는 사용하지 않음 |
| `file_path` | string \| null | 서버 로컬 스토리지 내 실제 파일 경로. 파일 전달의 소스 |
| `file_name` | string \| null | 저장된 파일명(확장자 포함). 사용자에게 노출되는 다운로드 파일명의 기준값 |
| `error_message` | string \| null | 본 기능에서는 사용하지 않음 |
| `created_at` | datetime | 본 기능에서는 사용하지 않음 |

**검증 규칙 (본 기능에서 추가)**:
- 파일 전달 요청 시 `status != completed` → 409 Conflict.
- `job_id`에 해당하는 작업이 존재하지 않음 → 404 Not Found.
- `status == completed`이지만 `file_path`가 가리키는 파일이 실제로 존재하지 않음(삭제/만료) → 404 Not Found.

## FileDeliveryRequest (논리적 개념, 비영속)

| 필드 | 타입 | 설명 |
|------|------|------|
| `job_id` | string (UUID) | 대상 다운로드 작업 식별자 (경로 파라미터) |
| `requested_at` | datetime | 요청 처리 시각 (로그 목적, 별도 저장 없음) |
| `result` | enum (`success`, `rejected_not_ready`, `not_found`) | 처리 결과 — HTTP 상태 코드(200/409/404)로 표현됨 |

이 엔티티는 데이터베이스나 메모리 저장소에 영속화되지 않으며, 단일 HTTP 요청-응답 처리 과정을 설명하기 위한 개념적 모델이다.

## 상태 전이 (참고, 001과 동일)

```
pending → downloading → processing → completed
                                   ↘ failed
```

본 기능은 `completed` 상태에 도달한 이후의 읽기 전용 파일 접근만 다루며, 상태 전이 자체에는 영향을 주지 않는다.
