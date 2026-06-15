import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import download, video


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("downloads", exist_ok=True)
    yield


app = FastAPI(
    title="유튜브 동영상 다운로더 API",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video.router, prefix="/api/video", tags=["video"])
app.include_router(download.router, prefix="/api/download", tags=["download"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
