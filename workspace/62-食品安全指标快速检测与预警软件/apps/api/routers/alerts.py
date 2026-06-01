# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from apps.api.schemas.alert import AlertAcknowledgeResponse, AlertView
from apps.api.services.store import Store

router = APIRouter(prefix="/api", tags=["alerts"])


def get_store() -> Store:
    app_db_path = Path(__file__).resolve().parents[3] / "data" / "app.db"
    return Store(db_path=app_db_path)


@router.get("/alerts", response_model=list[AlertView])
def list_alerts(store: Store = Depends(get_store)) -> list[AlertView]:
    store.seed_demo()
    rows = store.list_alerts()
    return [
        AlertView(
            alert_id=row.alert_id,
            sample_id=row.sample_id,
            alert_level=row.alert_level,
            reason=row.reason,
            status=row.status,
            created_at=row.created_at,
            acknowledged_at=row.acknowledged_at,
        )
        for row in rows
    ]


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertAcknowledgeResponse)
def acknowledge_alert(alert_id: str, store: Store = Depends(get_store)) -> AlertAcknowledgeResponse:
    updated = store.acknowledge_alert(alert_id)
    if not updated:
        raise HTTPException(status_code=404, detail="预警不存在或已确认")
    return AlertAcknowledgeResponse(alert_id=alert_id, status="已确认")
