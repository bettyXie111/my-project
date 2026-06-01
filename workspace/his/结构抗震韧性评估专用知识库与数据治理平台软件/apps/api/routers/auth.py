from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.authz import require_user
from ..core.db import get_conn
from ..core.security import TokenClaims, issue_token
from ..services.audit import audit_log


router = APIRouter(tags=["auth"])


class LoginIn(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def login(data: LoginIn) -> dict[str, str]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT username, role, display_name FROM users WHERE username=? AND password=?",
            (data.username, data.password),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="bad credentials")
        token = issue_token(subject=row["username"], role=row["role"])
        audit_log(conn, actor=row["username"], action="login", object_type="user", object_id=row["username"], detail="ok")
        return {"token": token, "role": row["role"], "display_name": row["display_name"]}


@router.get("/auth/me")
def me(claims: TokenClaims = Depends(require_user)) -> dict[str, str]:
    return {"username": claims.sub, "role": claims.role}

