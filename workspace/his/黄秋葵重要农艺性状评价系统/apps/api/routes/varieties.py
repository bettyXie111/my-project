from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.variety import VarietyCreate, VarietyItem, VarietyUpdate
from ..services.audit import write_audit
from ..services.varieties import (
    create_variety,
    get_variety,
    list_varieties,
    update_variety,
)


router = APIRouter(tags=["varieties"])


@router.get("/varieties", response_model=list[VarietyItem])
def api_list_varieties(q: str = "") -> list[VarietyItem]:
    return list_varieties(query=q.strip())


@router.get("/varieties/{variety_id}", response_model=VarietyItem)
def api_get_variety(variety_id: str) -> VarietyItem:
    item = get_variety(variety_id)
    if not item:
        raise HTTPException(status_code=404, detail="variety_not_found")
    return item


@router.post("/varieties", response_model=VarietyItem)
def api_create_variety(payload: VarietyCreate) -> VarietyItem:
    item = create_variety(payload)
    write_audit("variety.create", {"id": item.id, "name": item.name})
    return item


@router.put("/varieties/{variety_id}", response_model=VarietyItem)
def api_update_variety(variety_id: str, payload: VarietyUpdate) -> VarietyItem:
    item = update_variety(variety_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="variety_not_found")
    write_audit("variety.update", {"id": item.id})
    return item

