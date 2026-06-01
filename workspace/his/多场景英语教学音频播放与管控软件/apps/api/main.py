from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# When started via `python apps/api/main.py`, ensure repo root is importable.
if __package__ is None or __package__ == "":
    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root))

from apps.api.routers import auth, control, devices, lessons, scenes, stats


def create_app() -> FastAPI:
    app = FastAPI(title="多场景英语教学音频播放与管控软件 API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api")
    app.include_router(scenes.router, prefix="/api")
    app.include_router(devices.router, prefix="/api")
    app.include_router(lessons.router, prefix="/api")
    app.include_router(control.router, prefix="/api")
    app.include_router(stats.router, prefix="/api")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.mount("/", StaticFiles(directory="apps/web", html=True), name="web")
    return app


app = create_app()


def main() -> None:
    port = int(os.environ.get("APP_PORT", "8000"))
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
