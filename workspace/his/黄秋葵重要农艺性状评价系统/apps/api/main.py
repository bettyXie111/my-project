from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from apps.api.routes.audit import router as audit_router
from apps.api.routes.observations import router as observations_router
from apps.api.routes.scoring import router as scoring_router
from apps.api.routes.trials import router as trials_router
from apps.api.routes.traits import router as traits_router
from apps.api.routes.varieties import router as varieties_router
from apps.api.services.db import ensure_database


def create_app() -> FastAPI:
    ensure_database()
    app = FastAPI(
        title="黄秋葵重要农艺性状评价系统",
        version="1.0.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(varieties_router, prefix="/api")
    app.include_router(traits_router, prefix="/api")
    app.include_router(trials_router, prefix="/api")
    app.include_router(observations_router, prefix="/api")
    app.include_router(scoring_router, prefix="/api")
    app.include_router(audit_router, prefix="/api")

    web_root = Path(__file__).resolve().parents[1] / "web"
    if web_root.exists():
        app.mount("/", StaticFiles(directory=str(web_root), html=True), name="web")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8010, reload=False)
