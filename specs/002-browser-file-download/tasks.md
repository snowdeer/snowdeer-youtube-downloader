---

description: "Task list for 브라우저를 통한 다운로드 파일 전달"
---

# Tasks: 브라우저를 통한 다운로드 파일 전달

**Input**: Design documents from `/specs/002-browser-file-download/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: 헌법 원칙 I(TDD 우선 개발, NON-NEGOTIABLE)에 따라 모든 구현 작업에 대해 테스트를 먼저 작성한다(Red → Green).

**Organization**: 작업은 spec.md의 User Story 우선순위(P1 → P2 → P3)별로 그룹화되어 있다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 작업이 속한 User Story (US1, US2, US3)

## Path Conventions

웹 애플리케이션 구조 (001과 동일): `backend/app/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup

**Purpose**: 신규 의존성 없음 — 기존 001 프로젝트 구조를 그대로 사용

- [X] T001 기존 백엔드(`uv run pytest tests/ -v`)와 프론트엔드(`npm run test`) 테스트가 모두 Green 상태인지 확인하여 작업 시작 기준선을 확보

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: User Story 1, 2가 공통으로 의존하는 파일 조회/파일명 처리 로직

**⚠️ CRITICAL**: 이 단계 완료 전에는 어떤 User Story 작업도 시작할 수 없음

- [X] T002 [P] `backend/tests/unit/test_download_service.py`에 완료 작업 파일 조회 단위 테스트 작성 (존재하는 job_id/completed 상태 → 파일 경로 반환, 미존재 job_id → `LookupError`, 미완료 상태 → `RuntimeError`). 테스트가 FAIL 하는지 확인
- [X] T003 [P] `backend/tests/unit/test_download_service.py`에 `build_content_disposition(file_name)` 단위 테스트 작성 (한글/특수문자 포함 제목, ASCII fallback과 `filename*=UTF-8''...` 값 모두 검증). 테스트가 FAIL 하는지 확인
- [X] T004 `backend/app/services/download_service.py`에 `get_completed_file(job_id) -> tuple[str, str]` 메서드 추가: job_id 미존재 시 `LookupError`, `status != completed` 또는 파일이 실제로 존재하지 않으면 `RuntimeError`, 정상 시 `(file_path, file_name)` 반환 (T002 통과시키기)
- [X] T005 `backend/app/services/download_service.py`(또는 신규 `backend/app/core/file_naming.py`)에 `build_content_disposition(file_name: str) -> str` 헬퍼 추가: 파일 시스템/HTTP 헤더 금지 문자를 안전하게 치환한 ASCII fallback과 RFC 5987 `filename*` 값을 모두 포함한 `Content-Disposition` 헤더 문자열 생성 (T003 통과시키기)

**Checkpoint**: 파일 조회 및 파일명 헤더 생성 로직 준비 완료 — User Story 구현 시작 가능

---

## Phase 3: User Story 1 - 완료된 다운로드 파일을 브라우저로 받기 (Priority: P1) 🎯 MVP

**Goal**: 완료된 다운로드 작업의 파일을 브라우저를 통해 사용자 로컬 PC로 전달

**Independent Test**: 다운로드 작업을 완료 상태로 만든 뒤, 완료 화면의 다운로드 동작을 실행하면 브라우저가 파일을 로컬에 저장하는지 확인

### Tests for User Story 1 ⚠️

> **NOTE: 아래 테스트를 먼저 작성하고 FAIL 하는 것을 확인한 뒤 구현을 시작한다**

- [X] T006 [P] [US1] `backend/tests/integration/test_download_api.py`에 `GET /api/download/{job_id}/file` 통합 테스트 작성: (a) completed 작업 → 200 + 올바른 `Content-Type`(mp4→video/mp4, mp3→audio/mpeg) + 파일 바이트 일치, (b) 미존재 job_id → 404, (c) pending/downloading 상태 job_id → 409. 테스트가 FAIL 하는지 확인
- [X] T007 [P] [US1] `frontend/tests/components/DownloadResult.spec.ts`에 컴포넌트 테스트 작성: `status==='completed'`일 때만 다운로드 링크가 렌더링되고 `href`가 올바른 파일 다운로드 URL을 가리키는지 검증. 테스트가 FAIL 하는지 확인

### Implementation for User Story 1

- [X] T008 [US1] `backend/app/api/routes/download.py`에 `GET /{job_id}/file` 라우트 추가: `download_service.get_completed_file()` 호출 → `LookupError`는 404, `RuntimeError`는 409로 변환, 정상 시 `FileResponse`로 반환하며 `media_type`을 format에 따라 설정 (T004, T006 의존)
- [X] T009 [P] [US1] `frontend/src/services/api.ts`에 `getFileDownloadUrl(jobId: string): string` 헬퍼 추가 (`/api/download/{jobId}/file` 경로 반환)
- [X] T010 [US1] `frontend/src/components/DownloadResult.vue` 신규 생성: `status==='completed'`일 때 `getFileDownloadUrl(jobId)`를 가리키는 `<a download>` 링크 렌더링 (T009 의존, T007 통과시키기)
- [X] T011 [US1] `frontend/src/App.vue`에 `DownloadResult.vue`를 연결하여 `downloadStore.status === 'completed'`일 때 표시되도록 통합

**Checkpoint**: User Story 1 단독으로 완전히 동작 — 완료된 작업의 파일을 브라우저로 받을 수 있음

---

## Phase 4: User Story 2 - 원본 영상 제목 기반 파일명 (Priority: P2)

**Goal**: 브라우저가 저장을 제안하는 파일명이 원본 영상 제목 기반으로 식별 가능하게 함

**Independent Test**: 한글/특수문자가 포함된 제목의 영상을 다운로드 완료 후 받았을 때, 제안된 파일명이 제목을 식별 가능한 형태로 포함하는지 확인

### Tests for User Story 2 ⚠️

- [X] T012 [P] [US2] `backend/tests/integration/test_download_api.py`에 `GET /{job_id}/file` 응답의 `Content-Disposition` 헤더 검증 테스트 추가: 한글 제목 포함 작업에 대해 ASCII `filename`과 UTF-8 `filename*` 값이 모두 존재하고 올바르게 인코딩되었는지 확인. 테스트가 FAIL 하는지 확인

### Implementation for User Story 2

- [X] T013 [US2] `backend/app/api/routes/download.py`의 `GET /{job_id}/file` 응답에 `T005`의 `build_content_disposition()` 결과를 `Content-Disposition` 헤더로 설정 (T008, T012 의존)

**Checkpoint**: User Story 1 + 2 모두 독립적으로 동작 — 다운로드 파일이 식별 가능한 제목 기반 파일명으로 저장됨

---

## Phase 5: User Story 3 - 다운로드 중 전송 진행 표시 (Priority: P3)

**Goal**: 대용량 파일 전송 시에도 끊김 없이 끝까지 전달되고, 사용자가 전송 중임을 인지할 수 있음

**Independent Test**: 큰 파일을 다운로드할 때 전송이 중간에 끊기지 않고 완료되며, 받은 파일 크기가 원본과 일치하는지 확인

### Tests for User Story 3 ⚠️

- [X] T014 [P] [US3] `backend/tests/integration/test_download_api.py`에 `GET /{job_id}/file` 응답의 `Content-Length` 헤더가 실제 저장된 파일 크기와 일치하는지 검증하는 테스트 추가. 테스트가 FAIL 하는지 확인

### Implementation for User Story 3

- [X] T015 [US3] `backend/app/api/routes/download.py`의 `FileResponse` 사용이 청크 스트리밍으로 `Content-Length`를 자동 설정하는지 확인하고, 누락 시 명시적으로 설정 (T008, T014 의존)

**Checkpoint**: 모든 User Story가 독립적으로 동작 — 대용량 파일도 안정적으로 전달됨

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 전체 기능에 대한 마무리 검증

- [X] T016 [P] 코드 리뷰: `download_service.py`/`download.py`에 중복 로직이 없는지 확인하고 필요 시 추출 (헌법 II)
- [X] T017 `specs/002-browser-file-download/quickstart.md`의 모든 시나리오(1~6)를 수동으로 실행하여 통과 확인
- [X] T018 백엔드(`uv run pytest tests/ -v`)와 프론트엔드(`npm run test`) 전체 테스트 스위트가 Green 상태인지 최종 확인

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 — 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 시작. 모든 User Story를 BLOCK함
- **User Story 1 (Phase 3)**: Foundational 완료 후 시작 가능. 다른 Story에 의존하지 않음
- **User Story 2 (Phase 4)**: Foundational 완료 후 시작 가능하나, T013이 US1의 T008(라우트 자체)에 의존하므로 실질적으로 US1 이후 진행
- **User Story 3 (Phase 5)**: Foundational 완료 후 시작 가능하나, T015가 US1의 T008에 의존하므로 실질적으로 US1 이후 진행
- **Polish (Phase 6)**: 모든 User Story 완료 후 진행

### Parallel Opportunities

- T002, T003 (Foundational 테스트) 병렬 가능
- T006, T007 (US1 테스트) 병렬 가능
- T009 (US1 구현)는 T008과 병렬 가능 (다른 파일)
- T012 (US2 테스트), T014 (US3 테스트)는 서로 병렬 가능

---

## Parallel Example: Foundational + User Story 1

```bash
# Foundational 테스트 동시 작성:
Task: "단위 테스트 in backend/tests/unit/test_download_service.py (완료 작업 파일 조회)"
Task: "단위 테스트 in backend/tests/unit/test_download_service.py (Content-Disposition 헤더 생성)"

# User Story 1 테스트 동시 작성:
Task: "통합 테스트 in backend/tests/integration/test_download_api.py (GET /{job_id}/file)"
Task: "컴포넌트 테스트 in frontend/tests/components/DownloadResult.spec.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1만)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료 (필수 — 모든 Story를 막음)
3. Phase 3: User Story 1 완료
4. **STOP and VALIDATE**: quickstart.md 시나리오 1, 2, 4, 5로 독립 검증
5. 필요 시 배포/시연

### Incremental Delivery

1. Setup + Foundational 완료 → 기반 준비
2. User Story 1 추가 → 독립 검증 → 배포/시연 (MVP!)
3. User Story 2 추가 (파일명 식별성 개선) → 독립 검증 → 배포/시연
4. User Story 3 추가 (대용량 전송 안정성 검증) → 독립 검증 → 배포/시연
5. Polish 단계로 마무리

---

## Notes

- [P] 작업 = 다른 파일, 의존성 없음
- [Story] 라벨은 작업을 특정 User Story로 추적 가능하게 함
- 구현 전 테스트가 FAIL 하는지 반드시 확인 (헌법 I, TDD 비협상)
- 각 작업 또는 논리적 그룹 완료 후 커밋
- 체크포인트마다 멈춰서 해당 Story를 독립적으로 검증
