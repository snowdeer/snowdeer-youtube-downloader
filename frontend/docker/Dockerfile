# Stage 1: Vite 빌드
FROM node:20-alpine AS builder

WORKDIR /app

# 의존성 파일을 먼저 복사해 레이어 캐시 활용
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: nginx로 정적 파일 서빙
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
