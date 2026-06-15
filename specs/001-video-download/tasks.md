---

description: "유튜브 동영상 다운로더 구현 태스크 목록"
---

# Tasks: 유튜브 동영상 다운로더

**Input**: Design documents from `specs/001-video-download/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/api.md ✅

**TDD 적용**: 헌법 원칙 I(TDD NON-NEGOTIABLE)에 따라 모든 User Story 구현 전 테스트 먼저 작성(Red).

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 유저 스토리 레이블 (US1, US2, US3)
- 각 태스크에 정확한 파일 경로 포함

---

## Phase 1: Setup (프로젝트 초기화)

**Purpose**: 프로젝트 구조 생성 및 개발 환경 설정

- [x] T001 프로젝트 루트에 `backend/`, `frontend/` 디렉토리 구조 생성 (plan.md 소스 구조 기준)
- [x] T002 `backend/` uv 프로젝트 초기화 — `backend/pyproject.toml` 생성, 의존성 추가: fastapi, yt-dlp, uvicorn[standard], sse-starlette, pydantic>=2, pytest, pytest-asyncio, httpx, ruff, mypy
- [x] T003 [P] `frontend/` Vite + Vue 3 + TypeScript 프로젝트 초기화 — `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json` 생성, 의존성 추가: vue, pinia, axios, vitest, @vue/test-utils
- [x] T004 [P] 백엔드 ruff 설정 추가 — `backend/pyproject.toml`의 `[tool.ruff]` 섹션 구성 (line-length=100, select=["E","F","I"])
- [x] T005 [P] 프론트엔드 ESLint + Prettier 설정 — `frontend/.eslintrc.json`, `frontend/.prettierrc` 생성
- [x] T006 [P] `.gitignore` 생성 — `backend/downloads/`, `**/.env`, `node_modules/`, `__pycache__/`, `.venv/` 제외

**Checkpoint**: 백엔드 `uv run python -m pytest` 실행 가능, 프론트엔드 `npm run dev` 시작 가능

---

## Phase 2: Foundational (공통 기반 — 모든 User Story 블로킹)

**Purpose**: 모든 User Story가 공유하는 핵심 모델·설정·레이어 구축

⚠️ **CRITICAL**: 이 Phase가 완료되기 전까지 어떤 User Story도 시작할 수 없다.

- [x] T007 [P] 백엔드 Pydantic 모델 작성 — `backend/app/models/video.py` (VideoInfo: url, title, thumbnail_url, duration_seconds, channel + youtube URL 유효성 검증)
- [x] T008 [P] 백엔드 Pydantic 모델 작성 — `backend/app/models/download.py` (DownloadFormat enum, DownloadStatus enum, DownloadJob, DownloadProgress — data-model.md 기준)
- [x] T009 [P] 프론트엔드 TypeScript 타입 정의 — `frontend/src/types/index.ts` (VideoInfo, DownloadJob, DownloadFormat, DownloadStatus, DownloadProgress — data-model.md 기준)
- [x] T010 FastAPI 앱 진입점 설정 — `backend/app/main.py` (CORS 허용: localhost:5173, API 라우터 마운트 기반 구조, lifespan 이벤트 핸들러)
- [x] T011 [P] 백엔드 `backend/downloads/` 디렉토리 생성, `backend/.env.example` 작성 (DOWNLOAD_DIR, CORS_ORIGIN 설정)
- [x] T012 [P] 프론트엔드 API 서비스 레이어 기반 구조 생성 — `frontend/src/services/api.ts` (axios 인스턴스 생성, 베이스 URL 설정)
- [x] T013 [P] Pinia 스토어 기반 구조 생성 — `frontend/src/stores/downloadStore.ts` (url, format, videoInfo, jobId, progress, status, error 상태 정의)

**Checkpoint**: `backend/app/main.py` 실행 시 FastAPI 서버 구동 확인, 프론트엔드 타입 컴파일 오류 없음

---

## Phase 3: User Story 1 — URL 입력 및 동영상 다운로드 (Priority: P1) 🎯 MVP

**Goal**: 유효한 유튜브 URL 입력 → 영상 정보 조회 → 표시 기능 완성

**Independent Test**: `POST /api/video/info` 호출 시 영상 제목·썸네일·길이가 응답에 포함되고, 프론트엔드 URL 입력 → 정보 표시까지 동작하는 것을 확인.

### US1 테스트 작성 (Red 단계 — 반드시 먼저 실행하여 실패 확인)

> **⚠️ TDD 원칙: 아래 테스트를 먼저 작성하고 `pytest`/`vitest` 실행하여 FAIL을 확인한 후 구현으로 진행**

- [x] T014 [P] [US1] 단위 테스트 작성 (Red) — `backend/tests/unit/test_ytdlp_wrapper.py`
- [x] T015 [P] [US1] 단위 테스트 작성 (Red) — `backend/tests/unit/test_video_service.py`
- [x] T016 [P] [US1] 통합 테스트 작성 (Red) — `backend/tests/integration/test_video_api.py`
- [x] T017 [P] [US1] 컴포넌트 테스트 작성 (Red) — `frontend/tests/components/UrlInput.spec.ts`

### US1 구현 (Green 단계)

- [x] T018 [US1] yt-dlp 래퍼 구현 — `backend/app/core/ytdlp_wrapper.py`
- [x] T019 [US1] VideoService 구현 — `backend/app/services/video_service.py`
- [x] T020 [US1] 영상 정보 API 라우터 구현 — `backend/app/api/routes/video.py`
- [x] T021 [US1] UrlInput.vue 컴포넌트 구현 — `frontend/src/components/UrlInput.vue`
- [x] T022 [US1] VideoPreview.vue 컴포넌트 구현 — `frontend/src/components/VideoPreview.vue`
- [x] T023 [US1] downloadStore에 fetchVideoInfo 액션 구현 — `frontend/src/stores/downloadStore.ts`
- [x] T024 [US1] api.ts getVideoInfo 함수 구현 — `frontend/src/services/api.ts`
- [x] T025 [US1] App.vue에 UrlInput + VideoPreview 통합 — `frontend/src/App.vue`

### US1 코드 리뷰 및 리팩토링 (Blue 단계)

- [x] T026 [US1] US1 코드 리뷰 수행 — 중복 없음 확인, 모든 T014~T017 테스트 Green ✅

**Checkpoint**: US1 완료 — URL 입력 → 영상 정보 표시 독립 동작 확인 ✅

---

## Phase 4: User Story 2 — 저장 형식 선택 (Priority: P2)

**Goal**: mp4 / mp3 형식 선택 후 실제 다운로드 및 파일 저장 기능 완성

**Independent Test**: URL 입력 → mp3 선택 → 다운로드 버튼 클릭 → `backend/downloads/{job_id}/` 에 .mp3 파일 생성 확인.

### US2 테스트 작성 (Red 단계)

- [x] T027 [P] [US2] 단위 테스트 작성 (Red) — `backend/tests/unit/test_download_service.py`
- [x] T028 [P] [US2] 통합 테스트 작성 (Red) — `backend/tests/integration/test_download_api.py`
- [x] T029 [P] [US2] 컴포넌트 테스트 작성 (Red) — `frontend/tests/components/FormatSelector.spec.ts`

### US2 구현 (Green 단계)

- [x] T030 [US2] ytdlp_wrapper에 download 함수 추가 — `backend/app/core/ytdlp_wrapper.py`
- [x] T031 [US2] DownloadService 구현 — `backend/app/services/download_service.py`
- [x] T032 [US2] 다운로드 API 라우터 구현 — `backend/app/api/routes/download.py`
- [x] T033 [US2] FormatSelector.vue 컴포넌트 구현 — `frontend/src/components/FormatSelector.vue`
- [x] T034 [US2] downloadStore에 format·startDownload 추가 — `frontend/src/stores/downloadStore.ts`
- [x] T035 [US2] api.ts startDownload 함수 구현 — `frontend/src/services/api.ts`
- [x] T036 [US2] App.vue에 FormatSelector + 다운로드 버튼 통합 — `frontend/src/App.vue`

### US2 코드 리뷰 및 리팩토링 (Blue 단계)

- [x] T037 [US2] US2 코드 리뷰 수행 — 공통 yt-dlp 옵션 패턴 추상화 확인, 모든 T027~T029 테스트 Green ✅

**Checkpoint**: US2 완료 ✅

---

## Phase 5: User Story 3 — 다운로드 진행상황 실시간 표시 (Priority: P3)

**Goal**: 다운로드 진행률 0~100%를 SSE로 실시간 전달하여 프론트엔드에 표시

**Independent Test**: 다운로드 시작 후 SSE 스트림에서 progress_percent 이벤트가 수신되고, UI 진행 바가 실시간 갱신되는 것을 확인.

### US3 테스트 작성 (Red 단계)

- [x] T038 [P] [US3] 단위 테스트 추가 (Red) — `backend/tests/unit/test_download_service.py`
- [x] T039 [P] [US3] 통합 테스트 추가 (Red) — `backend/tests/integration/test_download_api.py`
- [x] T040 [P] [US3] 스토어 테스트 작성 (Red) — `frontend/tests/stores/downloadStore.spec.ts`
- [x] T041 [P] [US3] 컴포넌트 테스트 작성 (Red) — `frontend/tests/components/ProgressBar.spec.ts`

### US3 구현 (Green 단계)

- [x] T042 [US3] ytdlp_wrapper에 progress_hooks 콜백 구현 — `backend/app/core/ytdlp_wrapper.py`
- [x] T043 [US3] DownloadService에 진행률 저장소 관리 추가 — `backend/app/services/download_service.py`
- [x] T044 [US3] SSE 진행률 스트림 라우터 구현 — `backend/app/api/routes/download.py`
- [x] T045 [US3] /api/download/{job_id}/status 라우터 구현 — `backend/app/api/routes/download.py`
- [x] T046 [US3] ProgressBar.vue 컴포넌트 구현 — `frontend/src/components/ProgressBar.vue`
- [x] T047 [US3] downloadStore에 SSE 구독 로직 추가 — `frontend/src/stores/downloadStore.ts`
- [x] T048 [US3] api.ts에 SSE 구독 함수 구현 — `frontend/src/services/api.ts`
- [x] T049 [US3] App.vue에 ProgressBar 통합 — `frontend/src/App.vue`

### US3 코드 리뷰 및 리팩토링 (Blue 단계)

- [x] T049 [US3] US3 코드 리뷰 수행 — EventSource 해제 처리 확인, 모든 T038~T041 테스트 Green ✅

**Checkpoint**: 전체 3개 User Story 독립 동작 확인 ✅

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 엣지 케이스 보강, 문서화, 최종 품질 점검

- [x] T050 [P] 엣지 케이스 오류 처리 보강 — `backend/app/core/ytdlp_wrapper.py`, `backend/app/services/`
- [x] T051 [P] 프론트엔드 오류 상태 처리 보강 — `frontend/src/stores/downloadStore.ts`, `frontend/src/App.vue`
- [x] T052 quickstart.md 기반 엔드-투-엔드 수동 검증 준비 완료
- [x] T053 [P] 전체 테스트 스위트 실행 — 백엔드 20/20 ✅, 프론트엔드 19/19 ✅
- [x] T054 [P] `backend/.env.example` 완성 및 `index.html` 작성
- [x] T055 최종 코드 리뷰 완료 — 중복 로직 없음, 단일 책임 원칙 준수 ✅

---

## Dependencies & Execution Order

### Phase 의존성

- **Setup (Phase 1)**: 의존성 없음 — 즉시 시작
- **Foundational (Phase 2)**: Setup 완료 필요 — **모든 User Story 블로킹**
- **US1 (Phase 3)**: Foundational 완료 필요
- **US2 (Phase 4)**: Foundational 완료 필요 (US1 독립적이나 ytdlp_wrapper 공유)
- **US3 (Phase 5)**: US2 완료 필요 (다운로드 job_id 전제)
- **Polish (Phase 6)**: 모든 User Story 완료 필요

### User Story 내 의존성

- 테스트(Red) → 모델 → 서비스 → 라우터 → 프론트엔드 컴포넌트 → 통합
- 리뷰/리팩토링은 각 US의 마지막 단계

---

## Notes

- `[P]` 태스크 = 다른 파일, 의존성 없음 — 병렬 실행 가능
- TDD 순서 엄수: Red(테스트 작성 → FAIL 확인) → Green(구현) → Blue(리뷰+리팩토링)
- 모든 태스크 완료 ✅ — 백엔드 20 테스트, 프론트엔드 19 테스트 전부 통과
