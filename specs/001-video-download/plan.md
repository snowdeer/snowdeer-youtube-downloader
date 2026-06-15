# Implementation Plan: 유튜브 동영상 다운로더

**Branch**: `001-video-download` | **Date**: 2026-06-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-video-download/spec.md`

## Summary

유튜브 동영상 URL을 입력받아 mp4 또는 mp3 형식으로 다운로드하고, 실시간 진행률을 표시하는 웹 애플리케이션. Python/FastAPI 백엔드는 yt-dlp로 다운로드를 처리하고 SSE로 진행률을 스트리밍하며, Vue 3 프론트엔드는 사용자 인터페이스를 담당한다.

## Technical Context

**Language/Version**:
- 백엔드: Python 3.11+
- 프론트엔드: TypeScript 5.x (Node.js 20+)

**Primary Dependencies**:
- 백엔드: FastAPI, yt-dlp, uvicorn, sse-starlette, pydantic v2
- 패키지 관리: uv
- 프론트엔드: Vue 3, Vite, Pinia, Axios

**Storage**: 로컬 파일 시스템 (`backend/downloads/` 디렉토리)

**Testing**:
- 백엔드: pytest, pytest-asyncio, httpx
- 프론트엔드: Vitest, Vue Test Utils

**Target Platform**: 로컬 웹 서비스 (localhost 단일 사용자 환경)

**Project Type**: 웹 애플리케이션 (backend + frontend 분리 구조)

**Performance Goals**:
- 영상 정보 조회 응답 < 5초
- URL 유효성 오류 메시지 표시 < 3초
- 진행률 갱신 주기 ≤ 1초

**Constraints**:
- 동시 다운로드 1건 (v1)
- 단일 사용자 환경
- v1 지원 형식: mp4, mp3만

**Scale/Scope**: 단일 사용자, 로컬 개발/운영 환경, v1 MVP

## Constitution Check

*GATE: Phase 0 연구 전 반드시 통과해야 함. Phase 1 설계 후 재확인.*

| 원칙 | 상태 | 준수 계획 |
|------|------|-----------|
| I. TDD 우선 개발 | ✅ 통과 | 모든 구현 전 pytest/Vitest 테스트 먼저 작성. Red 확인 후 Green 구현 |
| II. 코드 리뷰 및 리팩토링 | ✅ 통과 | 각 User Story Green 완료 후 리뷰 수행. 중복 로직 추출 |
| III. 백엔드 아키텍처 | ✅ 통과 | FastAPI + yt-dlp. api → services → core 레이어 분리 |
| IV. 프론트엔드 아키텍처 | ✅ 통과 | Vue 3 Composition API + Vite + Pinia |
| V. 명확성 우선 설계 | ✅ 통과 | spec.md → plan.md → contracts/ 순서 준수 |

**게이트 결과**: 전 항목 통과 — 계획 진행 가능.

*Phase 1 설계 후 재확인 결과*: 모든 원칙 준수 확인. 복잡성 정당화 필요 항목 없음.

## Project Structure

### Documentation (this feature)

```text
specs/001-video-download/
├── plan.md              # 이 파일
├── research.md          # Phase 0 연구 결과
├── data-model.md        # Phase 1 데이터 모델
├── quickstart.md        # Phase 1 검증 가이드
├── contracts/           # Phase 1 API 계약
│   └── api.md
└── tasks.md             # Phase 2 작업 목록 (/speckit-tasks 생성)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── api/
│   │   └── routes/
│   │       ├── video.py     # 영상 정보 조회 라우터
│   │       └── download.py  # 다운로드 제어 라우터
│   ├── services/
│   │   ├── video_service.py    # 영상 정보 조회 비즈니스 로직
│   │   └── download_service.py # 다운로드 비즈니스 로직
│   ├── core/
│   │   └── ytdlp_wrapper.py    # yt-dlp 추상화 레이어
│   └── models/
│       ├── video.py         # VideoInfo Pydantic 모델
│       └── download.py      # DownloadJob Pydantic 모델
├── tests/
│   ├── unit/
│   │   ├── test_ytdlp_wrapper.py
│   │   ├── test_video_service.py
│   │   └── test_download_service.py
│   └── integration/
│       ├── test_video_api.py
│       └── test_download_api.py
├── downloads/               # 다운로드 파일 저장 디렉토리
├── pyproject.toml           # uv 기반 패키지 설정
└── .env.example

frontend/
├── src/
│   ├── App.vue
│   ├── main.ts
│   ├── components/
│   │   ├── UrlInput.vue       # URL 입력 컴포넌트
│   │   ├── FormatSelector.vue # 형식 선택 컴포넌트
│   │   ├── VideoPreview.vue   # 영상 정보 표시 컴포넌트
│   │   └── ProgressBar.vue    # 다운로드 진행률 컴포넌트
│   ├── stores/
│   │   └── downloadStore.ts   # Pinia 다운로드 상태 관리
│   ├── services/
│   │   └── api.ts             # 백엔드 API 호출 서비스
│   └── types/
│       └── index.ts           # TypeScript 타입 정의
├── tests/
│   ├── components/
│   │   ├── UrlInput.spec.ts
│   │   ├── FormatSelector.spec.ts
│   │   └── ProgressBar.spec.ts
│   └── stores/
│       └── downloadStore.spec.ts
├── vite.config.ts
├── package.json
└── tsconfig.json
```

**Structure Decision**: 헌법 원칙 III/IV에 따라 `backend/` + `frontend/` 분리 구조 채택. 백엔드는 api → services → core 3레이어 분리.

## Complexity Tracking

> 헌법 위반 항목 없음 — 정당화 필요 없음.
