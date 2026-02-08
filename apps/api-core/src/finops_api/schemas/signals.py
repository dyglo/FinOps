from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SignalFeatureRead(BaseModel):
    id: UUID
    org_id: UUID
    symbol: str
    feature_name: str
    feature_version: str
    value: float
    meta: dict[str, object]
    created_at: datetime
    updated_at: datetime