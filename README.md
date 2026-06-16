# snowdeer-youtube-downloader

유튜브 동영상 URL을 입력받아 mp4 또는 mp3 형식으로 다운로드하고, 브라우저를 통해 로컬 PC로 받을 수 있는 웹 애플리케이션입니다.

## 사전 요구사항

- Python 3.11 이상
- Node.js 20 이상
- [uv](https://docs.astral.sh/uv/) (Python 패키지 관리자)
- ffmpeg (mp3 변환에 필요)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`

## 설치 방법

### 백엔드

```bash
cd backend
uv sync
```

필요 시 `.env.example`을 참고하여 `.env` 파일을 생성합니다.

```bash
cp .env.example .env
```

| 환경 변수 | 설명 | 기본값 |
|-----------|------|--------|
| `DOWNLOAD_DIR` | 다운로드 파일 저장 경로 | `./downloads` |
| `CORS_ORIGIN` | 허용할 프론트엔드 출처 | `http://localhost:5173` |
| `MAX_CONCURRENT_DOWNLOADS` | 동시 다운로드 최대 개수 | `1` |

### 프론트엔드

```bash
cd frontend
npm install
```

## 실행 방법

### 백엔드 서버 실행

```bash
cd backend
uv run uvicorn app.main:app --reload --port 7990
```

정상적으로 실행되면 다음과 같은 로그가 출력됩니다.

```
INFO:     Uvicorn running on http://127.0.0.1:7990 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 프론트엔드 개발 서버 실행

```bash
cd frontend
npm run dev
```

정상적으로 실행되면 다음과 같은 로그가 출력됩니다.

```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

브라우저에서 `http://localhost:5173`에 접속하여 사용합니다. (프론트엔드는 `/api` 요청을 백엔드 `http://localhost:7990`으로 프록시합니다.)

## 테스트 실행

### 백엔드 테스트 (pytest)

```bash
cd backend
uv run pytest tests/ -v
```

### 프론트엔드 테스트 (Vitest)

```bash
cd frontend
npm run test
```

## 더 알아보기

각 기능의 상세 명세, 설계, 검증 가이드는 `specs/` 디렉터리를 참고하세요.

- [001-video-download](specs/001-video-download/quickstart.md): 유튜브 동영상 다운로더 핵심 기능
- [002-browser-file-download](specs/002-browser-file-download/quickstart.md): 브라우저를 통한 다운로드 파일 전달
