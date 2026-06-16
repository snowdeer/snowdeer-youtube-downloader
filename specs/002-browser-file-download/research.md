# Research: 브라우저를 통한 다운로드 파일 전달

**Date**: 2026-06-16
**Feature**: [spec.md](./spec.md)

Technical Context에 NEEDS CLARIFICATION 항목 없음. 아래는 설계 결정을 위한 핵심 조사 항목이다.

---

## 1. 파일 전송 방식

**Decision**: FastAPI의 `fastapi.responses.FileResponse`를 사용하여 파일을 스트리밍 응답으로 전달한다.

**Rationale**:
- `FileResponse`는 청크 단위 스트리밍을 지원하여 대용량 영상 파일도 메모리에 전체를 적재하지 않고 전송 가능 (SC-003, FR-009 충족).
- `Content-Length`, `ETag`, `Last-Modified` 헤더를 자동 설정하여 브라우저가 진행률/캐싱을 표준적으로 처리.
- 별도 외부 의존성 추가 없이 FastAPI/Starlette 표준 기능으로 해결 가능 (헌법 III: 검증된 라이브러리 우선).

**Alternatives considered**:
- `StreamingResponse` + 수동 파일 청크 읽기: `FileResponse`가 이미 동일한 효과를 제공하면서 코드가 더 단순함. 불필요한 복잡도 추가로 기각.
- 정적 파일 서버(Nginx 등) 별도 구성: 현재 단일 사용자 로컬 환경 규모에 비해 과도한 인프라 추가. 범위 외.

---

## 2. 파일명 지정 및 한글/특수문자 처리

**Decision**: `Content-Disposition: attachment; filename="<sanitized>"; filename*=UTF-8''<url-encoded>` 형식으로 응답 헤더를 구성한다. 파일명은 영상 제목에서 파일 시스템 금지 문자(`/ \ : * ? " < > |` 등)를 `_`로 치환하고, 길이를 제한(예: 200자)한 뒤 작업별 확장자(.mp4/.mp3)를 붙인다.

**Rationale**:
- RFC 5987의 `filename*` 확장 파라미터를 함께 제공하면 한글 등 비ASCII 제목도 대부분의 최신 브라우저에서 올바르게 표시됨 (FR-004, User Story 2 충족).
- ASCII `filename` fallback을 함께 제공하여 구형 브라우저에서도 다운로드가 실패하지 않도록 함.
- 001에서 이미 `DownloadJob.file_name`에 저장된 실제 저장 파일명을 기준으로 sanitize 로직을 재사용/확장.

**Alternatives considered**:
- 파일명을 `job_id` 그대로 사용: 구현은 단순하지만 사용자가 내용을 식별할 수 없어 User Story 2(SC-005)를 충족하지 못함. 기각.

---

## 3. 접근 제어 (소유권 판별)

**Decision**: 별도 인증 시스템이 없는 현재 범위에서, `job_id`(UUID v4)를 추측 불가능한 접근 토큰으로 간주한다. 파일 다운로드 요청 시 해당 `job_id`가 존재하고 상태가 `completed`인 경우에만 파일을 반환한다.

**Rationale**:
- 001 기능의 Assumptions에서 이미 단일 사용자/로컬 환경을 전제로 하고 있으며, 인증 시스템 도입은 범위 외.
- UUID는 충돌/추측 가능성이 매우 낮아 로컬 단일 사용자 환경에서 실질적인 접근 제어 수단으로 충분 (FR-007 충족, 과도한 설계 방지 — 헌법 II YAGNI).

**Alternatives considered**:
- 세션 기반 사용자 인증 추가: 001/002 모두 단일 사용자 로컬 도구로 정의되어 있어 현재 범위에서 불필요한 복잡도. 향후 다중 사용자 지원 시 별도 기능으로 고려.

---

## 4. 미완료/존재하지 않는 작업에 대한 오류 처리

**Decision**: 기존 `/download/{job_id}/status`, `/download/{job_id}/progress`와 동일한 오류 패턴을 따른다. `job_id` 미존재 시 404, 상태가 `completed`가 아닐 시 409(Conflict)로 응답한다.

**Rationale**:
- 001 contracts/api.md에서 이미 확립된 오류 응답 패턴(`{"detail": "..."}`)과 일관성 유지.
- 409는 "현재 리소스 상태와 요청이 충돌"하는 의미로, 진행 중/실패 작업에 대한 파일 요청 상황과 정확히 일치 (FR-002, FR-008 충족).

**Alternatives considered**:
- 모든 비정상 케이스를 404로 통일: 상태 구분이 사라져 클라이언트가 "존재하지 않음"과 "아직 준비 안 됨"을 구분할 수 없어 UX가 저하됨. 기각.

---

## 5. 프론트엔드 다운로드 트리거 방식

**Decision**: 작업 상태가 `completed`가 되면 `<a :href="fileDownloadUrl" download>` 형태의 네이티브 앵커 링크를 노출하여 브라우저 기본 다운로드 동작에 위임한다.

**Rationale**:
- 브라우저 네이티브 다운로드는 메모리에 전체 파일을 적재하는 `fetch` + `Blob` 방식보다 대용량 파일에 적합하고 구현이 단순함 (헌법 II: 불필요한 복잡도 제거).
- 브라우저가 자체 다운로드 진행 표시를 제공하므로 User Story 3(보조 기능)을 별도 구현 없이 충족.

**Alternatives considered**:
- `fetch` → `Blob` → `URL.createObjectURL` 방식: 대용량 파일 시 메모리 사용량이 커지고, 진행률 표시를 직접 구현해야 하는 추가 복잡도 발생. 현재 범위에서 불필요.
