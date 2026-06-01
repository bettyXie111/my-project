from __future__ import annotations

from fastapi import APIRouter

from packages.core.store import db

router = APIRouter(tags=["devices"])


@router.get("/devices")
def list_devices(scene_id: str | None = None) -> dict:
    items = db.list_devices(scene_id=scene_id)
    return {"items": items}
