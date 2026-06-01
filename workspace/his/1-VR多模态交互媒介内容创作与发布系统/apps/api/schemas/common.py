# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class IdResponse(BaseModel):
    id: str = Field(..., description="资源唯一标识")
