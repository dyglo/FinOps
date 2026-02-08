from __future__ import annotations

from datetime import UTC
from datetime import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, Field


class TwelveDataQuoteRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)


class TwelveDataTimeseriesRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    interval: str = Field(default='1day', min_length=2, max_length=16)
    outputsize: int = Field(default=100, ge=1, le=5000)
    start_date: str | None = None
    end_date: str | None = None


class TwelveDataQuoteResponse(BaseModel):
    symbol: str
    close: Decimal
    percent_change: Decimal | None = None
    datetime: str

    def as_of(self) -> dt:
        return parse_datetime(self.datetime)


class TwelveDataValue(BaseModel):
    datetime: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class TwelveDataMeta(BaseModel):
    symbol: str
    interval: str


class TwelveDataTimeseriesResponse(BaseModel):
    meta: TwelveDataMeta
    values: list[TwelveDataValue] = Field(default_factory=list)


class CanonicalTimeseriesPoint(BaseModel):
    symbol: str
    timeframe: str
    ts: dt
    open: float
    high: float
    low: float
    close: float
    volume: float


class CanonicalQuote(BaseModel):
    symbol: str
    price: float
    change_percent: float | None
    as_of: dt


def parse_datetime(value: str) -> dt:
    cleaned = value.strip()
    if len(cleaned) == 10:
        parsed = dt.fromisoformat(f'{cleaned}T00:00:00')
    else:
        parsed = dt.fromisoformat(cleaned.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
