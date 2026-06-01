from __future__ import annotations

from fastapi import APIRouter, HTTPException

from packages.core.auth import authenticate_user

router = APIRouter(tags=["auth"])


@router.post("/login")
def login(payload: dict) -> dict:
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    user = authenticate_user(username=username, password=password)
    if not user:
        raise HTTPException(status_code=401, detail="invalid_credentials")
    return {"token": f"demo-token:{user['id']}", "user": user}
