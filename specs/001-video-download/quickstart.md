# Quickstart 검증 가이드: 유튜브 동영상 다운로더

**Date**: 2026-06-15
**Feature**: specs/001-video-download/spec.md
**API Contract**: [contracts/api.md](./contracts/api.md)
**Data Model**: [data-model.md](./data-model.md)

이 가이드는 구현 완료 후 기능이 올바르게 동작하는지 검증하는 절차를 설명한다.

---

## 사전 요구사항

**시스템 의존성**:
- Python 3.11 이상
- Node.js 20 이상
- uv (`pip install uv` 또는 공식 설치)
- ffmpeg (mp3 변환 필요)
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`

---

## 백엔드 시작

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 7990
```

정상 시작 확인:
```
INFO:     Uvicorn running on http://127.0.0.1:7990 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## 프론트엔드 시작

```bash
cd frontend
npm install
npm run dev
```

정상 시작 확인:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

---

## 테스트 실행

**백엔드 테스트** (pytest):
```bash
cd backend
uv run pytest tests/ -v
```

**프론트엔드 테스트** (Vitest):
```bash
cd frontend
npm run test
```

---

## 기능 검증 시나리오

### 시나리오 1: 정상 mp4 다운로드 (User Story 1 & 2)

1. 브라우저에서 `http://localhost:5173` 접속
2. URL 입력 필드에 유효한 유튜브 URL 입력
   - 예시: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
3. 형식 선택에서 **mp4** 선택
4. 다운로드 버튼 클릭

**기대 결과**:
- 영상 제목, 썸네일, 재생 시간 표시
- 다운로드 진행률 바 표시 및 실시간 갱신
- `backend/downloads/{job_id}/` 에 `.mp4` 파일 생성

### 시나리오 2: mp3 음원 추출 (User Story 2)

1. 동일 URL 입력
2. 형식 선택에서 **mp3** 선택
3. 다운로드 버튼 클릭

**기대 결과**:
- `backend/downloads/{job_id}/` 에 `.mp3` 파일 생성

### 시나리오 3: 다운로드 진행상황 확인 (User Story 3)

- 다운로드 진행 중 진행률 바가 1초 이내 갱신 주기로 0% → 100% 변화 확인
- 완료 시 "완료" 상태 메시지 표시 확인

### 시나리오 4: 잘못된 URL 처리 (Edge Case)

1. URL 입력 필드에 `https://www.google.com` 입력
2. 다운로드 버튼 클릭

**기대 결과**:
- 3초 이내에 "유효한 유튜브 URL이 아닙니다" 오류 메시지 표시
- 다운로드 시작 안 됨

### 시나리오 5: API 직접 검증 (cURL)

```bash
# 영상 정보 조회
curl -X POST http://localhost:7990/api/video/info \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# 다운로드 시작
curl -X POST http://localhost:7990/api/download/start \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "format": "mp4"}'

# SSE 진행률 확인 (job_id 교체)
curl -N http://localhost:7990/api/download/{job_id}/progress
```

---

## 성공 기준 검증표

| 성공 기준 | 검증 방법 | 통과 조건 |
|-----------|-----------|-----------|
| SC-001: 5분 이내 완료 | 타이머 측정 | URL 입력부터 파일 생성까지 5분 미만 |
| SC-002: 3초 내 오류 표시 | 잘못된 URL 시나리오 | 3초 이내 오류 메시지 확인 |
| SC-003: 진행률 실시간 갱신 | 시각적 확인 | 1초 이내 갱신 주기 확인 |
| SC-004: 형식 정확도 | 파일 확인 | 선택 형식과 저장 파일 형식 일치 |
| SC-005: 영상 정보 5초 조회 | 타이머 측정 | URL 입력 후 5초 이내 정보 표시 |
