from __future__ import annotations

from datetime import UTC
from datetime import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, Field


class AlphaVantageQuoteRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)


class AlphaVantageTimeseriesRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    interval: str = Field(default='1day')
    outputsize: str = Field(default='compact', pattern='^(compact|full)$')


class AlphaVantageQuoteItem(BaseModel):
    symbol: str = Field(alias='01. symbol')
    price: Decimal = Field(alias='05. price')
    latest_trading_day: str = Field(alias='07. latest trading day')
    change_percent: str | None = Field(default=None, alias='10. change percent')


class AlphaVantageQuoteResponse(BaseModel):
    global_quote: AlphaVantageQuoteItem = Field(alias='Global Quote')


class AlphaVantageDailyValue(BaseModel):
    open: Decimal = Field(alias='1. open')
    high: Decimal = Field(alias='2. high')
    low: Decimal = Field(alias='3. low')
    close: Decimal = Field(alias='4. close')
    volume: Decimal = Field(alias='5. volume')


class AlphaVantageTimeseriesResponse(BaseModel):
    meta_data: dict[str, str] = Field(alias='Meta Data')
    daily: dict[str, AlphaVantageDailyValue] = Field(alias='Time Series (Daily)')


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


def parse_date(value: str) -> dt:
    parsed = dt.fromisoformat(value.strip())
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def parse_change_percent(value: str | None) -> float | None:
    if not value:
        return None
    return float(value.replace('%', '').strip())
