FROM python:3.11-slim

# ffmpeg: mp3 변환(오디오 추출)에 필요
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# uv 바이너리만 복사 (pip 없이 설치)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 의존성 파일을 먼저 복사해 레이어 캐시 활용
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 앱 소스 복사
COPY app/ ./app/

RUN mkdir -p downloads

EXPOSE 7990

CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7990"]
