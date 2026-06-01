from __future__ import annotations

from fastapi import APIRouter, HTTPException

from packages.core.store import db

router = APIRouter(tags=["scenes"])


@router.get("/scenes")
def list_scenes() -> dict:
    return {"items": db.list_scenes()}


@router.patch("/scenes/{scene_id}")
def patch_scene(scene_id: str, payload: dict) -> dict:
    caps = payload.get("capabilities")
    if not isinstance(caps, dict):
        raise HTTPException(status_code=400, detail="invalid_capabilities")
    item = db.update_scene_capabilities(scene_id=scene_id, capabilities=caps)
    if not item:
        raise HTTPException(status_code=404, detail="not_found")
    return {"item": item}
