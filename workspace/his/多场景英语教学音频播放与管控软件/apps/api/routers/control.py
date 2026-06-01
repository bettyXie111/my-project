from __future__ import annotations

from fastapi import APIRouter, HTTPException

from packages.core.store import db

router = APIRouter(tags=["control"])


@router.post("/lessons/{lesson_id}/start")
def start_lesson(lesson_id: str, payload: dict | None = None) -> dict:
    session = db.start_session(lesson_id=lesson_id)
    if not session:
        raise HTTPException(status_code=404, detail="lesson_not_found")
    return {"session": session}


@router.post("/sessions/{session_id}/end")
def end_session(session_id: str, payload: dict | None = None) -> dict:
    session = db.end_session(session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"session": session}


@router.post("/sessions/{session_id}/event")
def post_event(session_id: str, payload: dict) -> dict:
    action = str(payload.get("action", "")).strip()
    actor_user_id = str(payload.get("actor_user_id", "")).strip()
    target = str(payload.get("target", "all_students")).strip()
    if not action or not actor_user_id:
        raise HTTPException(status_code=400, detail="missing_fields")
    event = db.add_event(session_id=session_id, actor_user_id=actor_user_id, target=target, action=action, payload=payload.get("payload", {}))
    if not event:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"event": event}


@router.get("/sessions/{session_id}/events")
def list_events(session_id: str, since: int = 0) -> dict:
    items = db.list_events(session_id=session_id, since=since)
    return {"items": items}


@router.get("/sessions/{session_id}/policy")
def get_policy(session_id: str) -> dict:
    policy = db.get_session_policy(session_id)
    if not policy:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"policy": policy}
