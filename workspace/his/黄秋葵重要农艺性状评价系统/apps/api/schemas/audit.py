from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class AuditItem(BaseModel):
    id: str
    action: str
    payload: dict
    created_at: datetime

