from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.authz import TokenClaims, require_perm
from ..core.db import get_conn


router = APIRouter(tags=["audit"])


@router.get("/audit/logs")
def list_logs(limit: int = 200, _: TokenClaims = Depends(require_perm("audit:read"))) -> list[dict]:
    limit = max(1, min(500, int(limit)))
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

