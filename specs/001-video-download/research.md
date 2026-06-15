# Research: 유튜브 동영상 다운로더

**Date**: 2026-06-15
**Feature**: specs/001-video-download/spec.md

## 1. 실시간 진행률 전달 방식: SSE vs WebSocket

- **Decision**: SSE (Server-Sent Events) 사용
- **Rationale**: 다운로드 진행률 전달은 서버 → 클라이언트 단방향 스트림이다. SSE는 WebSocket 대비 구현이 단순하고, FastAPI에서 `sse-starlette` 라이브러리로 쉽게 지원된다. WebSocket의 양방향 통신 능력은 이 사용 사례에서 불필요하다.
- **Alternatives Considered**:
  - WebSocket: 양방향이므로 과도한 복잡성. yt-dlp 진행률이 단방향이므로 부적합.
  - 폴링(Polling): SSE 대비 지연 발생, 불필요한 HTTP 요청 오버헤드.
- **Implementation Note**: `GET /api/download/{job_id}/progress` 엔드포인트를 SSE 스트림으로 구현. `sse-starlette` 라이브러리 사용.

## 2. yt-dlp 비동기 호출 방식

- **Decision**: `asyncio.run_in_executor` + `ThreadPoolExecutor` 사용
- **Rationale**: yt-dlp는 동기(synchronous) 라이브러리다. FastAPI의 비동기 이벤트 루프를 블로킹하지 않으려면 별도 스레드에서 실행해야 한다. `run_in_executor`는 표준 라이브러리로 추가 의존성 없이 사용 가능하다.
- **Alternatives Considered**:
  - Celery + Redis: 태스크 큐 시스템 도입 → v1 단일 사용자 환경에서 과도한 복잡성.
  - subprocess로 yt-dlp CLI 호출: 프로세스 간 통신 복잡, 타입 안전성 없음.
- **Implementation Note**: `core/ytdlp_wrapper.py`에서 `loop.run_in_executor(executor, download_func, ...)` 패턴 사용.

## 3. yt-dlp 진행률 콜백 연동

- **Decision**: yt-dlp `progress_hooks` 옵션 사용 + 공유 딕셔너리로 상태 전달
- **Rationale**: yt-dlp는 `ydl_opts`에 `progress_hooks` 콜백 리스트를 받는다. 콜백 함수에서 진행률(%) 데이터를 메모리 내 딕셔너리(`job_id → progress`)에 업데이트하면, SSE 스트림에서 폴링하여 클라이언트에 전달 가능하다.
- **Alternatives Considered**:
  - Redis pub/sub: 외부 의존성 추가 필요, v1 범위 초과.
  - asyncio.Queue: 스레드 간 공유 시 thread-safety 이슈.
- **Implementation Note**: `download_service.py`에서 `Dict[str, int]` 타입의 `_progress_store` 딕셔너리 관리. `threading.Lock`으로 동시성 보호.

## 4. 파일 저장 경로 전략

- **Decision**: `backend/downloads/{job_id}/` 디렉토리에 저장
- **Rationale**: job_id별 서브 디렉토리로 파일 충돌 방지. 파일명은 yt-dlp가 생성한 영상 제목 기반 이름 사용.
- **Alternatives Considered**:
  - 단일 `downloads/` 디렉토리: 동일 제목 파일 충돌 위험.
  - 사용자 지정 경로: v1 범위 외, UX 복잡도 증가.
- **Implementation Note**: `job_id`는 `uuid4()` 생성. `.gitignore`에 `backend/downloads/` 추가.

## 5. URL 유효성 검사 전략

- **Decision**: 프론트엔드 정규식 선검사 + 백엔드 yt-dlp 실제 검증
- **Rationale**: 헌법 원칙 IV에 따라 프론트엔드에서 먼저, 백엔드에서 최종 검증. 프론트엔드는 유튜브 URL 패턴 정규식으로 즉각적인 피드백 제공. 백엔드는 yt-dlp `extract_info`로 실제 접근 가능 여부 확인.
- **유튜브 URL 패턴**: `https://(www.)?youtube.com/watch?v=`, `https://youtu.be/`
- **Alternatives Considered**:
  - 백엔드 전용 검증: 네트워크 요청 후에야 오류 표시 → UX 저하.

## 6. 다운로드 형식 옵션

- **Decision**: mp4 (최고 화질 자동 선택) + mp3 (192kbps 음원 추출)
- **Rationale**: v1 MVP는 가장 일반적인 두 형식만 지원. yt-dlp `format` 옵션으로 제어.
- **yt-dlp 옵션**:
  - mp4: `format: 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'`
  - mp3: `format: 'bestaudio/best'`, `postprocessors: [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]`
- **Note**: mp3 변환을 위해 `ffmpeg` 시스템 의존성 필요. quickstart.md에 설치 지침 포함.

## 7. 프론트엔드 상태 관리 설계

- **Decision**: Pinia store 1개 (`downloadStore`) + API 서비스 레이어 분리
- **Rationale**: 헌법 원칙 IV 준수. 다운로드 상태(URL, 선택 형식, 진행률, VideoInfo)를 단일 store에서 관리. API 호출은 `services/api.ts`에 분리하여 테스트 용이성 확보.
- **Store 상태**: `url`, `format`, `videoInfo`, `jobId`, `progress`, `status`, `error`

## 요약: 핵심 기술 결정

| 항목 | 결정 | 근거 |
|------|------|------|
| 실시간 통신 | SSE | 단방향, 구현 단순 |
| yt-dlp 호출 | run_in_executor | 비동기 블로킹 방지 |
| 진행률 공유 | 메모리 딕셔너리 | v1 단순성 |
| 파일 저장 | job_id 서브디렉토리 | 파일명 충돌 방지 |
| URL 검사 | FE 정규식 + BE yt-dlp | 헌법 원칙 IV |
| 다운로드 형식 | mp4 + mp3 | MVP 범위 |
