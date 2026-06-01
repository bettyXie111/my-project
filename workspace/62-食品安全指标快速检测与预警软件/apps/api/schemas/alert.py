# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class AlertView(BaseModel):
    alert_id: str
    sample_id: str
    alert_level: str
    reason: str
    status: str
    created_at: str
    acknowledged_at: str | None = None


class AlertAcknowledgeResponse(BaseModel):
    alert_id: str = Field(..., description="预警编号")
    status: str = Field(..., description="确认结果")
