# Quickstart 검증 가이드: 브라우저를 통한 다운로드 파일 전달

**Date**: 2026-06-16
**Feature**: specs/002-browser-file-download/spec.md
**API Contract**: [contracts/api.md](./contracts/api.md)
**Data Model**: [data-model.md](./data-model.md)

이 가이드는 구현 완료 후 기능이 올바르게 동작하는지 검증하는 절차를 설명한다. 001 기능(다운로드 자체)이 선행되어 있어야 한다.

---

## 사전 요구사항

001 quickstart.md와 동일한 환경(Python 3.11+, Node.js 20+, uv, ffmpeg)이 갖춰져 있어야 한다.

---

## 백엔드 / 프론트엔드 시작

001과 동일하게 시작한다.

```bash
# 백엔드
cd backend && uv run uvicorn app.main:app --reload --port 7990

# 프론트엔드
cd frontend && npm run dev
```

---

## 테스트 실행

```bash
cd backend && uv run pytest tests/ -v
cd frontend && npm run test
```

---

## 기능 검증 시나리오

### 시나리오 1: 완료된 파일을 브라우저로 다운로드 (User Story 1)

1. `http://localhost:5173` 접속 후 유효한 유튜브 URL 입력, mp4 선택, 다운로드 실행
2. 작업 상태가 "완료"로 바뀔 때까지 대기
3. 화면에 표시된 다운로드 버튼/링크 클릭

**기대 결과**:
- 브라우저가 파일 전송을 시작하고 기본 다운로드 폴더에 파일이 저장됨
- 저장된 파일을 재생했을 때 원본 영상과 동일한 내용(영상+음성)이 재생됨

### 시나리오 2: mp3 형식 다운로드 (User Story 1)

1. 동일 URL로 mp3 형식 선택 후 다운로드 완료까지 대기
2. 다운로드 버튼 클릭

**기대 결과**:
- 받은 파일 확장자가 `.mp3`이며 음원만 재생됨

### 시나리오 3: 영상 제목 기반 파일명 확인 (User Story 2)

1. 한글 또는 특수문자가 포함된 제목의 영상을 다운로드 완료 후 파일 받기

**기대 결과**:
- 브라우저가 저장을 제안하는 파일명이 영상 제목을 식별 가능한 형태로 포함 (금지 문자는 안전하게 치환됨)

### 시나리오 4: 미완료 작업에 대한 다운로드 시도 (Edge Case, FR-002)

```bash
# 다운로드 시작 직후(아직 completed 상태가 아닐 때) 파일 요청
curl -i http://localhost:7990/api/download/{job_id}/file
```

**기대 결과**:
- HTTP 409 응답과 "다운로드가 아직 완료되지 않았습니다" 메시지

### 시나리오 5: 존재하지 않는 작업 요청 (Edge Case, FR-008)

```bash
curl -i http://localhost:7990/api/download/00000000-0000-0000-0000-000000000000/file
```

**기대 결과**:
- HTTP 404 응답과 "해당 다운로드 작업을 찾을 수 없습니다" 메시지

### 시나리오 6: API 직접 검증 (cURL, 정상 케이스)

```bash
# 1) 다운로드 시작 (001 절차)
curl -X POST http://localhost:7990/api/download/start \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "format": "mp4"}'

# 2) status가 completed가 될 때까지 폴링 (job_id 교체)
curl http://localhost:7990/api/download/{job_id}/status

# 3) 완료 후 파일 다운로드 (응답 헤더 확인)
curl -i -OJ http://localhost:7990/api/download/{job_id}/file
```

**기대 결과**:
- `Content-Disposition` 헤더에 영상 제목 기반 파일명이 포함됨
- 다운로드된 파일 크기가 서버 `backend/downloads/` 내 원본 파일 크기와 일치

---

## 성공 기준 검증표

| 성공 기준 | 검증 방법 | 통과 조건 |
|-----------|-----------|-----------|
| SC-001: 완료 작업 100% 다운로드 가능 | 시나리오 1, 2 | 모든 completed 작업에서 다운로드 버튼 동작 |
| SC-002: 클릭 후 1초 내 전송 시작 | 브라우저 네트워크 탭 확인 | 클릭 후 1초 이내 응답 시작(TTFB) |
| SC-003: 파일 무결성 100% | 파일 크기/재생 확인 | 원본과 동일한 크기 및 정상 재생 |
| SC-004: 미완료/존재하지 않는 작업 오류 100% | 시나리오 4, 5 | 모든 케이스에서 409/404와 명확한 메시지 |
| SC-005: 제목만으로 식별 가능 | 시나리오 3 | 파일명에서 영상 제목 식별 가능 |
