# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends

from apps.api.schemas.sample import SampleCreate, SampleView
from apps.api.services.store import Store

router = APIRouter(prefix="/api", tags=["samples"])


def get_store() -> Store:
    app_db_path = Path(__file__).resolve().parents[3] / "data" / "app.db"
    return Store(db_path=app_db_path)


@router.get("/samples", response_model=list[SampleView])
def list_samples(store: Store = Depends(get_store)) -> list[SampleView]:
    store.seed_demo()
    rows = store.list_samples()
    return [
        SampleView(
            sample_id=r.sample_id,
            sample_code=r.sample_code,
            owner=r.owner,
            category_count=r.category_count,
            review_rounds=r.review_rounds,
            quantity=r.quantity,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/samples", response_model=dict[str, str])
def create_sample(dto: SampleCreate, store: Store = Depends(get_store)) -> dict[str, str]:
    sample_id = f"SMP-{uuid.uuid4().hex[:8].upper()}"
    store.create_sample(
        sample_id=sample_id,
        sample_code=dto.sample_code,
        owner=dto.owner,
        category_count=dto.category_count,
        review_rounds=dto.review_rounds,
        quantity=dto.quantity,
    )
    return {"sample_id": sample_id}
