from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TimeseriesPointRead(BaseModel):
    id: UUID
    org_id: UUID
    symbol: str
    timeframe: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float