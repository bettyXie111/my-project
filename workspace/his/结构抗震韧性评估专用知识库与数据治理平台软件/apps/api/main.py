from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# build_materials.py starts the server via: `python apps/api/main.py`
# When executed as a script, we need repo-root on sys.path so `apps.*` imports work.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.api.core.db import init_db  # noqa: E402
from apps.api.core.seed import ensure_seeded  # noqa: E402
from apps.api.routers import (  # noqa: E402
    assessments,
    audit,
    auth,
    datasets,
    indicators,
    knowledge,
    projects,
    quality,
    structures,
)


def create_app() -> FastAPI:
    app = FastAPI(title="结构抗震韧性评估专用知识库与数据治理平台软件", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router, prefix="/api")
    app.include_router(projects.router, prefix="/api")
    app.include_router(structures.router, prefix="/api")
    app.include_router(datasets.router, prefix="/api")
    app.include_router(quality.router, prefix="/api")
    app.include_router(indicators.router, prefix="/api")
    app.include_router(assessments.router, prefix="/api")
    app.include_router(knowledge.router, prefix="/api")
    app.include_router(audit.router, prefix="/api")

    return app


app = create_app()

init_db()
ensure_seeded()

app.mount("/", StaticFiles(directory="apps/web", html=True), name="web")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8010, log_level="warning")
