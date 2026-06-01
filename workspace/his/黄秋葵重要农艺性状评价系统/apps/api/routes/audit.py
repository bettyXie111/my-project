from __future__ import annotations

from fastapi import APIRouter

from ..schemas.audit import AuditItem
from ..services.audit import list_audit


router = APIRouter(tags=["audit"])


@router.get("/audit", response_model=list[AuditItem])
def api_list_audit(limit: int = 200) -> list[AuditItem]:
    limit = max(1, min(1000, int(limit)))
    return list_audit(limit=limit)

