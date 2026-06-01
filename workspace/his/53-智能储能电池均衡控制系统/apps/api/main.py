# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]

from apps.api.routers import health_router, packs_router


APP_NAME = '智能储能电池均衡控制系统'


def create_app() -> "FastAPI":
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install dependencies before running the API.")
    app = FastAPI(title=APP_NAME)

    app.include_router(health_router)
    app.include_router(packs_router)

    web_root = Path(__file__).resolve().parents[1] / "web"
    app.mount("/static", StaticFiles(directory=str(web_root)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return (web_root / "index.html").read_text(encoding="utf-8")

    return app


app = create_app()


def _main() -> None:
    import uvicorn

    port = int(os.environ.get("APP_PORT", "8000"))
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    _main()
