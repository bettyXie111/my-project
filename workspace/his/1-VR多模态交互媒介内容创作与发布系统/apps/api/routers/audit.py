# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from apps.api.services import audit_repo


router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[dict])
def list_audit(limit: int = 100):
    return audit_repo.list_audit(limit=limit)
