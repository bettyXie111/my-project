# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends

from apps.api.schemas.pack import PackCreate, PackView
from apps.api.services.store import Store


router = APIRouter(prefix="/api", tags=["packs"])


def get_store() -> Store:
    project_root = __import__("pathlib").Path(__file__).resolve().parents[3]
    data_dir = project_root / "data"
    db_path = data_dir / "app.db"
    return Store(db_path=db_path)


@router.get("/packs", response_model=list[PackView])
def list_packs(store: Store = Depends(get_store)) -> list[PackView]:
    store.seed_demo()
    rows = store.list_packs()
    return [
        PackView(
            pack_id=r.pack_id,
            pack_code=r.pack_code,
            vendor=r.vendor,
            series_cells=r.series_cells,
            parallel_cells=r.parallel_cells,
            rated_capacity_ah=r.rated_capacity_ah,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/packs", response_model=dict[str, str])
def create_pack(dto: PackCreate, store: Store = Depends(get_store)) -> dict[str, str]:
    pack_id = f"PACK-{uuid.uuid4().hex[:8].upper()}"
    store.create_pack(
        pack_id=pack_id,
        pack_code=dto.pack_code,
        vendor=dto.vendor,
        series_cells=dto.series_cells,
        parallel_cells=dto.parallel_cells,
        rated_capacity_ah=dto.rated_capacity_ah,
    )
    return {"pack_id": pack_id}
