# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from apps.api.schemas.asset import AssetCreate, AssetOut
from apps.api.services import asset_repo


router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("", response_model=list[AssetOut])
def list_assets(project_id: str):
    return asset_repo.list_assets(project_id)


@router.post("", response_model=dict)
def create_asset(payload: AssetCreate):
    aid = asset_repo.create_asset(
        payload.project_id,
        payload.type,
        payload.filename,
        payload.sha256,
        payload.size,
        payload.tags,
        payload.meta_json,
    )
    return {"id": aid}


@router.delete("/{asset_id}", response_model=dict)
def delete_asset(asset_id: str):
    ok = asset_repo.delete_asset(asset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
