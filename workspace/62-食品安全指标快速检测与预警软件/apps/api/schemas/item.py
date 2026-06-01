# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    item_code: str = Field(..., description="条目编号")
    owner: str = Field(..., description="归属方")
    category_count: int = Field(..., ge=1, le=400, description="分类数量")
    review_rounds: int = Field(..., ge=1, le=40, description="复核轮次")
    quantity: float = Field(..., gt=0, description="数量")


class ItemView(BaseModel):
    item_id: str
    item_code: str
    owner: str
    category_count: int
    review_rounds: int
    quantity: float
    created_at: str
