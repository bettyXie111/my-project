from __future__ import annotations

from fastapi import APIRouter, HTTPException

from packages.core.store import db

router = APIRouter(tags=["stats"])


@router.get("/lessons/{lesson_id}/stats")
def lesson_stats(lesson_id: str) -> dict:
    stats = db.lesson_stats(lesson_id=lesson_id)
    if not stats:
        raise HTTPException(status_code=404, detail="not_found")
    return {"stats": stats}
