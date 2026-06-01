from __future__ import annotations

from fastapi import APIRouter, HTTPException

from packages.core.store import db

router = APIRouter(tags=["lessons"])


@router.get("/lessons")
def list_lessons() -> dict:
    return {"items": db.list_lessons()}


@router.post("/lessons")
def create_lesson(payload: dict) -> dict:
    title = str(payload.get("title", "")).strip()
    scene_id = str(payload.get("scene_id", "")).strip()
    teacher_id = str(payload.get("teacher_id", "")).strip()
    if not title or not scene_id or not teacher_id:
        raise HTTPException(status_code=400, detail="missing_fields")
    item = db.create_lesson(title=title, scene_id=scene_id, teacher_id=teacher_id, book_unit=str(payload.get("book_unit", "")).strip())
    return {"item": item}


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: str) -> dict:
    item = db.get_lesson(lesson_id)
    if not item:
        raise HTTPException(status_code=404, detail="not_found")
    return {"item": item}


@router.get("/lessons/{lesson_id}/clips")
def list_clips(lesson_id: str) -> dict:
    return {"items": db.list_clips(lesson_id)}


@router.post("/lessons/{lesson_id}/clips")
def create_clip(lesson_id: str, payload: dict) -> dict:
    label = str(payload.get("label", "")).strip()
    start_ms = int(payload.get("start_ms", 0))
    end_ms = int(payload.get("end_ms", 0))
    asset_id = str(payload.get("audio_asset_id", "")).strip()
    if not label or not asset_id or end_ms <= start_ms:
        raise HTTPException(status_code=400, detail="invalid_clip")
    item = db.create_clip(
        lesson_id=lesson_id,
        audio_asset_id=asset_id,
        label=label,
        start_ms=start_ms,
        end_ms=end_ms,
        default_speed=float(payload.get("default_speed", 1.0)),
        loop_suggest=int(payload.get("loop_suggest", 1)),
    )
    return {"item": item}


@router.post("/lessons/{lesson_id}/end")
def end_lesson(lesson_id: str) -> dict:
    session = db.end_active_session(lesson_id=lesson_id)
    if not session:
        raise HTTPException(status_code=404, detail="not_found")
    return {"session": session}
