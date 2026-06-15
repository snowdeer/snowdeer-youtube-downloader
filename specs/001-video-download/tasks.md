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

- [ ] T001 프로젝트 루트에 `backend/`, `frontend/` 디렉토리 구조 생성 (plan.md 소스 구조 기준)
- [ ] T002 `backend/` uv 프로젝트 초기화 — `backend/pyproject.toml` 생성, 의존성 추가: fastapi, yt-dlp, uvicorn[standard], sse-starlette, pydantic>=2, pytest, pytest-asyncio, httpx, ruff, mypy
- [ ] T003 [P] `frontend/` Vite + Vue 3 + TypeScript 프로젝트 초기화 — `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json` 생성, 의존성 추가: vue, pinia, axios, vitest, @vue/test-utils
- [ ] T004 [P] 백엔드 ruff 설정 추가 — `backend/pyproject.toml`의 `[tool.ruff]` 섹션 구성 (line-length=100, select=["E","F","I"])
- [ ] T005 [P] 프론트엔드 ESLint + Prettier 설정 — `frontend/.eslintrc.json`, `frontend/.prettierrc` 생성
- [ ] T006 [P] `.gitignore` 생성 — `backend/downloads/`, `**/.env`, `node_modules/`, `__pycache__/`, `.venv/` 제외

**Checkpoint**: 백엔드 `uv run python -m pytest` 실행 가능, 프론트엔드 `npm run dev` 시작 가능

---

## Phase 2: Foundational (공통 기반 — 모든 User Story 블로킹)

**Purpose**: 모든 User Story가 공유하는 핵심 모델·설정·레이어 구축

⚠️ **CRITICAL**: 이 Phase가 완료되기 전까지 어떤 User Story도 시작할 수 없다.

- [ ] T007 [P] 백엔드 Pydantic 모델 작성 — `backend/app/models/video.py` (VideoInfo: url, title, thumbnail_url, duration_seconds, channel + youtube URL 유효성 검증)
- [ ] T008 [P] 백엔드 Pydantic 모델 작성 — `backend/app/models/download.py` (DownloadFormat enum, DownloadStatus enum, DownloadJob, DownloadProgress — data-model.md 기준)
- [ ] T009 [P] 프론트엔드 TypeScript 타입 정의 — `frontend/src/types/index.ts` (VideoInfo, DownloadJob, DownloadFormat, DownloadStatus, DownloadProgress — data-model.md 기준)
- [ ] T010 FastAPI 앱 진입점 설정 — `backend/app/main.py` (CORS 허용: localhost:5173, API 라우터 마운트 기반 구조, lifespan 이벤트 핸들러)
- [ ] T011 [P] 백엔드 `backend/downloads/` 디렉토리 생성, `backend/.env.example` 작성 (DOWNLOAD_DIR, CORS_ORIGIN 설정)
- [ ] T012 [P] 프론트엔드 API 서비스 레이어 기반 구조 생성 — `frontend/src/services/api.ts` (axios 인스턴스 생성, 베이스 URL 설정)
- [ ] T013 [P] Pinia 스토어 기반 구조 생성 — `frontend/src/stores/downloadStore.ts` (url, format, videoInfo, jobId, progress, status, error 상태 정의)

**Checkpoint**: `backend/app/main.py` 실행 시 FastAPI 서버 구동 확인, 프론트엔드 타입 컴파일 오류 없음

---

## Phase 3: User Story 1 — URL 입력 및 동영상 다운로드 (Priority: P1) 🎯 MVP

**Goal**: 유효한 유튜브 URL 입력 → 영상 정보 조회 → 표시 기능 완성

**Independent Test**: `POST /api/video/info` 호출 시 영상 제목·썸네일·길이가 응답에 포함되고, 프론트엔드 URL 입력 → 정보 표시까지 동작하는 것을 확인.

### US1 테스트 작성 (Red 단계 — 반드시 먼저 실행하여 실패 확인)

> **⚠️ TDD 원칙: 아래 테스트를 먼저 작성하고 `pytest`/`vitest` 실행하여 FAIL을 확인한 후 구현으로 진행**

- [ ] T014 [P] [US1] 단위 테스트 작성 (Red) — `backend/tests/unit/test_ytdlp_wrapper.py`: `get_video_info`가 유효 URL에서 VideoInfo 반환, 잘못된 URL에서 예외 발생 검증 (yt-dlp 모킹)
- [ ] T015 [P] [US1] 단위 테스트 작성 (Red) — `backend/tests/unit/test_video_service.py`: `VideoService.get_video_info`가 ytdlp_wrapper를 호출하고 VideoInfo 반환, 오류 전파 검증
- [ ] T016 [P] [US1] 통합 테스트 작성 (Red) — `backend/tests/integration/test_video_api.py`: `POST /api/video/info` 유효 URL 200 응답, 잘못된 URL 422 응답, 미존재 영상 404 응답 (httpx AsyncClient 사용)
- [ ] T017 [P] [US1] 컴포넌트 테스트 작성 (Red) — `frontend/tests/components/UrlInput.spec.ts`: URL 입력 렌더링, 유효한 URL 입력 시 이벤트 발행, 잘못된 URL 시 오류 메시지 표시 검증

### US1 구현 (Green 단계)

- [ ] T018 [US1] yt-dlp 래퍼 구현 — `backend/app/core/ytdlp_wrapper.py`: `get_video_info(url: str) -> VideoInfo` 함수 (asyncio.run_in_executor + ThreadPoolExecutor 사용, yt-dlp extract_info 호출)
- [ ] T019 [US1] VideoService 구현 — `backend/app/services/video_service.py`: `get_video_info(url: str) -> VideoInfo` 메서드 (ytdlp_wrapper 의존성 주입)
- [ ] T020 [US1] 영상 정보 API 라우터 구현 — `backend/app/api/routes/video.py`: `POST /api/video/info` 엔드포인트 (VideoService 호출, 오류 처리 — contracts/api.md 기준)
- [ ] T021 [US1] UrlInput.vue 컴포넌트 구현 — `frontend/src/components/UrlInput.vue`: URL 입력 필드, 유튜브 URL 정규식 유효성 검사, 오류 메시지 표시 (Composition API)
- [ ] T022 [US1] VideoPreview.vue 컴포넌트 구현 — `frontend/src/components/VideoPreview.vue`: 제목, 썸네일, 재생 시간 표시 (videoInfo prop)
- [ ] T023 [US1] downloadStore에 fetchVideoInfo 액션 구현 — `frontend/src/stores/downloadStore.ts`: url 상태 업데이트, API 호출, videoInfo·error 상태 갱신
- [ ] T024 [US1] api.ts getVideoInfo 함수 구현 — `frontend/src/services/api.ts`: `POST /api/video/info` 호출, VideoInfo 응답 반환
- [ ] T025 [US1] App.vue에 UrlInput + VideoPreview 통합 — `frontend/src/App.vue`: UrlInput 이벤트 → store.fetchVideoInfo → VideoPreview 표시 흐름 연결

### US1 코드 리뷰 및 리팩토링 (Blue 단계)

- [ ] T026 [US1] US1 코드 리뷰 수행 — 체크리스트: 중복 로직 제거, ytdlp_wrapper 인터페이스 명확성, 오류 메시지 일관성, 모든 T014~T017 테스트 Green 확인. 필요 시 리팩토링 적용

**Checkpoint**: US1 완료 — URL 입력 → 영상 정보 표시 독립 동작 확인

---

## Phase 4: User Story 2 — 저장 형식 선택 (Priority: P2)

**Goal**: mp4 / mp3 형식 선택 후 실제 다운로드 및 파일 저장 기능 완성

**Independent Test**: URL 입력 → mp3 선택 → 다운로드 버튼 클릭 → `backend/downloads/{job_id}/` 에 .mp3 파일 생성 확인.

### US2 테스트 작성 (Red 단계)

> **⚠️ TDD 원칙: 테스트 먼저 작성하고 FAIL 확인 후 구현 진행**

- [ ] T027 [P] [US2] 단위 테스트 작성 (Red) — `backend/tests/unit/test_download_service.py`: `DownloadService.start_download`가 DownloadJob 생성, status 전이(pending→downloading→completed) 검증, mp4·mp3 형식별 yt-dlp 옵션 확인 (모킹)
- [ ] T028 [P] [US2] 통합 테스트 작성 (Red) — `backend/tests/integration/test_download_api.py`: `POST /api/download/start` 202 응답 + job_id 반환, 중복 요청 409 응답, 잘못된 형식 422 응답 검증
- [ ] T029 [P] [US2] 컴포넌트 테스트 작성 (Red) — `frontend/tests/components/FormatSelector.spec.ts`: mp4·mp3 옵션 렌더링, 선택 시 change 이벤트 발행, 기본 선택값(mp4) 검증

### US2 구현 (Green 단계)

- [ ] T030 [US2] ytdlp_wrapper에 download 함수 추가 — `backend/app/core/ytdlp_wrapper.py`: `download_video(url, format, output_dir, progress_hook) -> str` (mp4: bestvideo+bestaudio, mp3: FFmpegExtractAudio 192kbps — research.md 기준)
- [ ] T031 [US2] DownloadService 구현 — `backend/app/services/download_service.py`: `start_download(url, format) -> DownloadJob`, `get_job(job_id) -> DownloadJob`, _jobs 딕셔너리 관리, 동시 1건 제한 (threading.Lock)
- [ ] T032 [US2] 다운로드 API 라우터 구현 — `backend/app/api/routes/download.py`: `POST /api/download/start` (DownloadService 호출, 백그라운드 태스크 시작), `GET /api/download/{job_id}/status` (contracts/api.md 기준)
- [ ] T033 [US2] FormatSelector.vue 컴포넌트 구현 — `frontend/src/components/FormatSelector.vue`: mp4·mp3 선택 UI (라디오 버튼 또는 드롭다운), 선택값 emit
- [ ] T034 [US2] downloadStore에 format·startDownload 추가 — `frontend/src/stores/downloadStore.ts`: format 상태, jobId 상태, startDownload 액션 (API 호출 후 jobId 저장)
- [ ] T035 [US2] api.ts startDownload 함수 구현 — `frontend/src/services/api.ts`: `POST /api/download/start` 호출, DownloadJob 응답 반환
- [ ] T036 [US2] App.vue에 FormatSelector + 다운로드 버튼 통합 — `frontend/src/App.vue`: FormatSelector 연결, 다운로드 버튼 → store.startDownload 호출

### US2 코드 리뷰 및 리팩토링 (Blue 단계)

- [ ] T037 [US2] US2 코드 리뷰 수행 — 체크리스트: ytdlp_wrapper의 mp4/mp3 공통 로직 추출 가능 여부, DownloadService 책임 범위 적절성, 모든 T027~T029 테스트 Green 확인. 필요 시 리팩토링 적용

**Checkpoint**: US2 완료 — URL 입력 → 형식 선택 → 다운로드 시작 → 파일 생성 독립 동작 확인

---

## Phase 5: User Story 3 — 다운로드 진행상황 실시간 표시 (Priority: P3)

**Goal**: 다운로드 진행률 0~100%를 SSE로 실시간 전달하여 프론트엔드에 표시

**Independent Test**: 다운로드 시작 후 SSE 스트림에서 progress_percent 이벤트가 수신되고, UI 진행 바가 실시간 갱신되는 것을 확인.

### US3 테스트 작성 (Red 단계)

> **⚠️ TDD 원칙: 테스트 먼저 작성하고 FAIL 확인 후 구현 진행**

- [ ] T038 [P] [US3] 단위 테스트 추가 (Red) — `backend/tests/unit/test_download_service.py`: progress_hook 콜백 호출 시 _progress_store 업데이트 검증, get_progress(job_id) 반환값 검증
- [ ] T039 [P] [US3] 통합 테스트 추가 (Red) — `backend/tests/integration/test_download_api.py`: `GET /api/download/{job_id}/progress` SSE 스트림이 DownloadProgress JSON 이벤트를 전송하고 completed 시 종료되는 것 검증
- [ ] T040 [P] [US3] 스토어 테스트 작성 (Red) — `frontend/tests/stores/downloadStore.spec.ts`: subscribeToProgress 호출 시 progress·status 상태 갱신, completed 시 SSE 연결 종료 검증
- [ ] T041 [P] [US3] 컴포넌트 테스트 작성 (Red) — `frontend/tests/components/ProgressBar.spec.ts`: progress prop 0~100 렌더링, 상태별 메시지 표시(다운로드 중/완료/실패) 검증

### US3 구현 (Green 단계)

- [ ] T042 [US3] ytdlp_wrapper에 progress_hooks 콜백 구현 — `backend/app/core/ytdlp_wrapper.py`: yt-dlp progress_hooks 옵션에 콜백 등록, downloaded_bytes/total_bytes로 percent 계산, 콜백 함수 인자로 수신하여 외부에서 주입 가능하도록 설계
- [ ] T043 [US3] DownloadService에 진행률 저장소 관리 추가 — `backend/app/services/download_service.py`: `_progress_store: Dict[str, DownloadProgress]`, `get_progress(job_id) -> DownloadProgress`, threading.Lock으로 동시성 보호
- [ ] T044 [US3] SSE 진행률 스트림 라우터 구현 — `backend/app/api/routes/download.py`: `GET /api/download/{job_id}/progress` SSE 엔드포인트 (sse-starlette EventSourceResponse, 1초 폴링, completed/failed 시 스트림 종료)
- [ ] T045 [US3] ProgressBar.vue 컴포넌트 구현 — `frontend/src/components/ProgressBar.vue`: progress(0~100) + status prop, 진행 바 너비 동적 적용, 상태 메시지(다운로드 중/변환 중/완료/실패) 표시
- [ ] T046 [US3] downloadStore에 SSE 구독 로직 추가 — `frontend/src/stores/downloadStore.ts`: `subscribeToProgress(jobId)` — EventSource 생성, onmessage 핸들러에서 progress·status 갱신, completed/failed 시 EventSource 종료
- [ ] T047 [US3] api.ts에 SSE 구독 함수 구현 — `frontend/src/services/api.ts`: `createProgressStream(jobId): EventSource` 함수 (브라우저 EventSource API 사용, URL: `/api/download/{jobId}/progress`)
- [ ] T048 [US3] App.vue에 ProgressBar 통합 — `frontend/src/App.vue`: startDownload 완료 후 subscribeToProgress 자동 시작, ProgressBar 컴포넌트 표시

### US3 코드 리뷰 및 리팩토링 (Blue 단계)

- [ ] T049 [US3] US3 코드 리뷰 수행 — 체크리스트: SSE 연결 해제 처리(컴포넌트 unmount 시), EventSource 에러 핸들링, progress_store 메모리 누수 방지, 모든 T038~T041 테스트 Green 확인. 필요 시 리팩토링 적용

**Checkpoint**: 전체 3개 User Story 독립 동작 확인

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 엣지 케이스 보강, 문서화, 최종 품질 점검

- [ ] T050 [P] 엣지 케이스 오류 처리 보강 — `backend/app/core/ytdlp_wrapper.py`, `backend/app/services/`: 비공개/지역제한 영상, 네트워크 단절, 디스크 공간 부족 예외 처리 및 사용자 친화적 오류 메시지 (spec.md Edge Cases 기준)
- [ ] T051 [P] 프론트엔드 오류 상태 처리 보강 — `frontend/src/stores/downloadStore.ts`, `frontend/src/App.vue`: 네트워크 오류 시 오류 메시지 표시, SSE 연결 실패 시 재시도 또는 폴백
- [ ] T052 quickstart.md 기반 엔드-투-엔드 수동 검증 실행 — 5개 시나리오 전부 통과 확인 후 체크 (`specs/001-video-download/quickstart.md`)
- [ ] T053 [P] 전체 테스트 스위트 실행 및 통과 확인 — `cd backend && uv run pytest tests/ -v`, `cd frontend && npm run test`
- [ ] T054 [P] `backend/.env.example` 완성 및 `README.md` 작성 — 실행 방법, 의존성(ffmpeg 포함), 환경 변수 설명
- [ ] T055 최종 코드 리뷰 (헌법 원칙 II 준수) — 전체 코드베이스 중복 로직 점검: ytdlp_wrapper 공통 패턴, store/api 중복 코드, 단일 책임 원칙 위반 여부. 발견 시 리팩토링 후 테스트 Green 재확인

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

### 병렬 실행 기회

- Phase 1: T002 ↔ T003 ↔ T004 ↔ T005 ↔ T006 병렬 가능
- Phase 2: T007 ↔ T008 ↔ T009 ↔ T011 ↔ T012 ↔ T013 병렬 가능
- 각 US 테스트 작성(Red): T014 ↔ T015 ↔ T016 ↔ T017 병렬 가능

---

## Implementation Strategy

### MVP (User Story 1만)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료
3. Phase 3: US1 완료 (테스트→구현→리뷰)
4. **STOP & VALIDATE**: URL 입력 → 영상 정보 표시 독립 동작 확인

### 순차 전달 (권장)

1. Setup + Foundational → 기반 준비
2. US1 (P1) → 검증 → **MVP!**
3. US2 (P2) → 검증 (형식 선택 + 다운로드)
4. US3 (P3) → 검증 (진행률 실시간 표시)
5. Polish → 최종 품질 점검

---

## Notes

- `[P]` 태스크 = 다른 파일, 의존성 없음 — 병렬 실행 가능
- `[USn]` 레이블 = 해당 User Story 트레이서빌리티
- TDD 순서 엄수: Red(테스트 작성 → FAIL 확인) → Green(구현) → Blue(리뷰+리팩토링)
- 각 User Story는 독립적으로 완료·검증 가능
- Phase 2 완료 전 US 작업 시작 금지
- 리팩토링 후 반드시 전체 테스트 Green 상태 재확인
