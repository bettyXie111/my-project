# -*- coding: utf-8 -*-
from __future__ import annotations

try:
    from fastapi import FastAPI
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]

from apps.api.routers.hr import router as hr_router


def create_app() -> "FastAPI":
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install dependencies before running the API.")
    app = FastAPI(title="API")
    app.include_router(hr_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
