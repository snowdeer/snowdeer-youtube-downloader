# CHANGELOG

이 프로젝트의 주요 변경 이력을 날짜 역순으로 기록합니다.

---

## [미배포] - 2026-06-18 (2)

### 기능 추가

- **Docker 빌드 지원**
  - `backend/docker/Dockerfile` — Python 3.11-slim + ffmpeg + uv 기반 백엔드 이미지
  - `frontend/docker/Dockerfile` — Node 20 빌드 → nginx Alpine 서빙 (멀티스테이지)
  - `frontend/docker/nginx.conf` — Vue Router history mode 지원, `/api/` → 백엔드 프록시, SSE 버퍼링 비활성화
  - `build_docker.sh` — 백엔드/프론트엔드 이미지를 순서대로 빌드하는 스크립트
  - `docker-compose.yaml` — 두 컨테이너를 함께 실행. 다운로드 파일은 `backend/downloads/`에 바인드 마운트로 유지

### 버그 수정

- **프론트엔드 빌드 실패** (`frontend/src/components/UrlInput.vue`)
  - `noUnusedLocals: true` 설정으로 인해 미사용 `props` 변수가 TypeScript 오류를 발생시켜 `npm run build` 실패
  - 수정: `const props = withDefaults(...)` → `withDefaults(...)` (템플릿에서만 props 참조하므로 변수 할당 불필요)

---

## [미배포] - 2026-06-18

### 버그 수정

- **브라우저 다운로드 버튼이 "파일을 다운로드할 수 없습니다" 오류를 표시하는 문제**
  - 증상: 다운로드 완료 후 버튼을 눌러도 에러 문구만 뜨고 파일이 받아지지 않음
  - 원인 1: `HEAD /api/download/{job_id}/file` 가 **405 Method Not Allowed** 반환
    → FastAPI `@router.get()` 은 HEAD 메서드를 자동 등록하지 않음
    → 수정: `backend/app/api/routes/download.py` 에 `@router.head("/{job_id}/file")` 명시적 추가
  - 원인 2: 프론트엔드에서 HEAD 성공 후 `document.createElement('a').click()` 을 DOM에 추가하지 않고 호출하면 브라우저가 무시함
    → 수정: `window.location.href = fileUrl` 로 변경. `Content-Disposition: attachment` 응답이므로 페이지 이동 없이 파일이 저장됨

---

## [미배포] - 2026-06-16

### 기능 추가

- **브라우저를 통한 다운로드 파일 전달** (Feature 002)
  - 유튜브에서 서버로 다운로드된 파일을 브라우저를 통해 로컬 PC로 받을 수 있도록 구현
  - 백엔드: `GET /api/download/{job_id}/file` 엔드포인트 추가 (`FileResponse` 스트리밍)
  - 백엔드: `build_content_disposition()` — 한글/특수문자 제목도 RFC 5987 규격으로 파일명 지정
  - 프론트엔드: 다운로드 완료 시 `DownloadResult.vue` 컴포넌트에 다운로드 링크 표시

### 변경

- **백엔드 포트 변경**: `8000` → `7990`
  - `frontend/vite.config.ts` 프록시 타깃 변경
  - 실행 명령: `uv run uvicorn app.main:app --reload --port 7990`

### 버그 수정

- **다운로드 시 `file.json` 파일이 저장되는 문제** (`frontend/src/components/DownloadResult.vue`)
  - 증상: 다운로드 버튼 클릭 시 음원/영상 파일 대신 `file.json`이 저장됨
  - 원인: 백엔드가 오류(404/409) JSON을 반환할 때 브라우저가 그대로 저장함
  - 수정: 클릭 시 HEAD 요청으로 파일 존재 여부를 먼저 확인하고, 오류 시 화면에 에러 메시지 표시

- **mp3 다운로드 시 "파일을 찾을 수 없습니다" 오류**
  - 증상: mp3 형식으로 다운로드 완료 후 파일 다운로드 버튼을 누르면 "다운로드 파일을 찾을 수 없습니다" 오류 발생
  - 원인 1: yt-dlp의 `prepare_filename()` 이 ffmpeg 후처리(mp3 변환) 전의 경로(`.webm`)를 반환함
    → `backend/app/core/ytdlp_wrapper.py`: 후처리 후 갱신되는 `info["filepath"]` 를 우선 사용하도록 수정
  - 원인 2: 확장자 불일치 등의 엣지 케이스 대비
    → `backend/app/services/download_service.py`: `_resolve_actual_file()` 추가 — 저장된 경로가 없으면 같은 디렉터리에서 실제 파일을 탐색해 자동 복구

---

## [0.1.0] - 2026-06-15

### 기능 추가 (Feature 001 초기 구현)

- 유튜브 URL 입력 및 영상 정보(제목, 썸네일, 재생시간) 조회
- mp4 / mp3 형식 선택 후 다운로드
- SSE(Server-Sent Events)로 다운로드 진행률 실시간 표시
- 백엔드: FastAPI + yt-dlp + Python 3.10+
- 프론트엔드: Vue 3 + Vite + Pinia + TypeScript
