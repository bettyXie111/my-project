from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.trait import TraitCreate, TraitItem, TraitUpdate
from ..services.audit import write_audit
from ..services.traits import create_trait, get_trait, list_traits, update_trait


router = APIRouter(tags=["traits"])


@router.get("/traits", response_model=list[TraitItem])
def api_list_traits(q: str = "") -> list[TraitItem]:
    return list_traits(query=q.strip())


@router.get("/traits/{trait_id}", response_model=TraitItem)
def api_get_trait(trait_id: str) -> TraitItem:
    item = get_trait(trait_id)
    if not item:
        raise HTTPException(status_code=404, detail="trait_not_found")
    return item


@router.post("/traits", response_model=TraitItem)
def api_create_trait(payload: TraitCreate) -> TraitItem:
    item = create_trait(payload)
    write_audit("trait.create", {"id": item.id, "code": item.code})
    return item


@router.put("/traits/{trait_id}", response_model=TraitItem)
def api_update_trait(trait_id: str, payload: TraitUpdate) -> TraitItem:
    item = update_trait(trait_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="trait_not_found")
    write_audit("trait.update", {"id": item.id})
    return item

