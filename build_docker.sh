#!/bin/bash
set -e

BACKEND_IMAGE="snowdeer-yt-downloader-backend"
FRONTEND_IMAGE="snowdeer-yt-downloader-frontend"

echo "=========================================="
echo " snowdeer-youtube-downloader Docker 빌드"
echo "=========================================="
echo ""

echo "[1/2] 백엔드 이미지 빌드 중..."
docker build \
  -t "$BACKEND_IMAGE" \
  -f backend/docker/Dockerfile \
  backend/

echo ""
echo "[2/2] 프론트엔드 이미지 빌드 중..."
docker build \
  -t "$FRONTEND_IMAGE" \
  -f frontend/docker/Dockerfile \
  frontend/

echo ""
echo "=========================================="
echo " 빌드 완료"
echo "=========================================="
echo "  백엔드  : $BACKEND_IMAGE"
echo "  프론트  : $FRONTEND_IMAGE"
echo ""
echo "실행하려면:"
echo "  docker-compose up"
echo ""
