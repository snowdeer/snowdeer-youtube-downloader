# Implementation Plan: 브라우저를 통한 다운로드 파일 전달

**Branch**: `002-browser-file-download` | **Date**: 2026-06-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-browser-file-download/spec.md`

## Summary

001 기능에서 서버 로컬 스토리지(`backend/downloads/`)에 저장된 다운로드 완료 파일을 사용자의 브라우저를 통해 로컬 PC로 전달한다. 백엔드는 새로운 파일 다운로드 엔드포인트(`GET /api/download/{job_id}/file`)를 추가하여 `FileResponse`로 파일을 스트리밍하고, 원본 영상 제목 기반의 안전한 파일명을 `Content-Disposition` 헤더로 지정한다. 프론트엔드는 작업이 `completed` 상태가 되면 다운로드 링크/버튼을 노출하여 브라우저 기본 다운로드 동작을 트리거한다.

## Technical Context

**Language/Version**:
- 백엔드: Python 3.11+
- 프론트엔드: TypeScript 5.x (Node.js 20+)

**Primary Dependencies**:
- 백엔드: FastAPI(`FileResponse`), 기존 `download_service`/`DownloadJob` 재사용
- 프론트엔드: Vue 3, Pinia, Axios (기존 `api.ts`/`downloadStore.ts` 확장)

**Storage**: 로컬 파일 시스템 (`backend/downloads/`, 001에서 이미 저장된 파일을 그대로 읽어 전달)

**Testing**:
- 백엔드: pytest, pytest-asyncio, httpx
- 프론트엔드: Vitest, Vue Test Utils

**Target Platform**: 로컬 웹 서비스 (localhost 단일 사용자 환경, 001과 동일)

**Project Type**: 웹 애플리케이션 (backend + frontend 분리 구조, 001 구조 확장)

**Performance Goals**:
- 다운로드 버튼 클릭 후 1초 이내 브라우저 파일 전송 시작
- 대용량 파일도 끊김 없이 끝까지 전송

**Constraints**:
- 별도 인증 시스템 없음 — `job_id`(UUID, 추측 불가능한 값)를 소유권 판별 토큰으로 사용
- 파일 보관/만료 정책의 구체적 수치는 범위 외 (존재하지 않는 파일에 대한 오류 처리만 포함)
- 서버측 Range/이어받기 로직 신규 구현 없음 (FastAPI `FileResponse`의 표준 동작에 위임)

**Scale/Scope**: 단일 사용자, 로컬 개발/운영 환경, 001의 다운로드 흐름에 이어지는 후속 단계 기능

## Constitution Check

*GATE: Phase 0 연구 전 반드시 통과해야 함. Phase 1 설계 후 재확인.*

| 원칙 | 상태 | 준수 계획 |
|------|------|-----------|
| I. TDD 우선 개발 | ✅ 통과 | 파일 전달 엔드포인트와 프론트엔드 다운로드 트리거 모두 테스트(pytest/httpx, Vitest) 먼저 작성 후 구현 |
| II. 코드 리뷰 및 리팩토링 | ✅ 통과 | 파일명 sanitize 로직은 기존 `download_service` 내 공유 유틸로 추출, 중복 방지 |
| III. 백엔드 아키텍처 | ✅ 통과 | api → services → core 레이어 유지. 새 라우트는 기존 `download.py`에 추가, 파일 경로 조회는 `download_service`에 위임 |
| IV. 프론트엔드 아키텍처 | ✅ 통과 | 기존 `downloadStore`/`api.ts` 확장, 새 UI는 단일 책임의 다운로드 링크/버튼으로 한정 |
| V. 명확성 우선 설계 | ✅ 통과 | spec.md → plan.md → contracts/api.md 순서로 인터페이스 선확정 |

**게이트 결과**: 전 항목 통과 — 계획 진행 가능.

*Phase 1 설계 후 재확인 결과*: 모든 원칙 준수 확인. 복잡성 정당화 필요 항목 없음.

## Project Structure

### Documentation (this feature)

```text
specs/002-browser-file-download/
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
│   ├── api/
│   │   └── routes/
│   │       └── download.py        # GET /{job_id}/file 라우트 추가
│   ├── services/
│   │   └── download_service.py    # 완료 파일 경로 조회 + 파일명 sanitize 로직 추가
│   └── models/
│       └── download.py            # 기존 DownloadJob.file_path/file_name 재사용 (변경 없음)
├── tests/
│   ├── unit/
│   │   └── test_download_service.py   # sanitize/파일 경로 조회 단위 테스트 추가
│   └── integration/
│       └── test_download_api.py       # 파일 다운로드 엔드포인트 통합 테스트 추가

frontend/
├── src/
│   ├── components/
│   │   └── DownloadResult.vue     # 완료 시 다운로드 링크/버튼을 보여주는 신규 컴포넌트
│   ├── stores/
│   │   └── downloadStore.ts       # 완료 상태에서 다운로드 URL 노출용 getter 추가
│   └── services/
│       └── api.ts                 # getFileDownloadUrl 헬퍼 추가
├── tests/
│   └── components/
│       └── DownloadResult.spec.ts # 신규 컴포넌트 테스트
```

**Structure Decision**: 001에서 확립한 `backend/` + `frontend/` 분리 구조와 백엔드 api → services → core 레이어를 그대로 유지하며, 새 기능은 신규 파일 추가를 최소화하고 기존 모듈(`download.py`, `download_service.py`, `downloadStore.ts`, `api.ts`)을 확장하는 방식으로 구현한다. 프론트엔드에는 단일 책임을 위해 `DownloadResult.vue` 컴포넌트만 신규 추가한다.

## Complexity Tracking

> 헌법 위반 항목 없음 — 정당화 필요 없음.
