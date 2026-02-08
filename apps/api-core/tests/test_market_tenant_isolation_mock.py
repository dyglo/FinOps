from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import Depends
from fastapi.testclient import TestClient

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.main import app


@dataclass
class DummySession:
    org_id: UUID


@dataclass
class TimeseriesRow:
    id: UUID
    org_id: UUID
    symbol: str
    timeframe: str
    provider: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    fetched_at: datetime


@dataclass
class QuoteRow:
    id: UUID
    org_id: UUID
    symbol: str
    provider: str
    price: float
    change_percent: float | None
    as_of: datetime
    fetched_at: datetime


class FakeMarketStore:
    timeseries: list[TimeseriesRow] = []
    quotes: list[QuoteRow] = []


class FakeMarketRepository:
    def __init__(self, session: DummySession) -> None:
        self._session = session

    async def get_timeseries(
        self,
        *,
        org_id: UUID,
        symbol: str,
        timeframe: str | None,
        start: datetime | None,
        end: datetime | None,
        limit: int,
    ) -> list[TimeseriesRow]:
        _ = (start, end)
        rows = [
            row
            for row in FakeMarketStore.timeseries
            if row.org_id == org_id and row.org_id == self._session.org_id and row.symbol == symbol
        ]
        if timeframe:
            rows = [row for row in rows if row.timeframe == timeframe]
        return rows[:limit]

    async def get_latest_quote(self, *, org_id: UUID, symbol: str) -> QuoteRow | None:
        rows = [
            row
            for row in FakeMarketStore.quotes
            if row.org_id == org_id and row.org_id == self._session.org_id and row.symbol == symbol
        ]
        return rows[0] if rows else None


async def override_tenant_session(org_id: UUID = Depends(get_org_id)):
    yield DummySession(org_id=org_id)


def test_market_endpoints_enforce_tenant_isolation(monkeypatch) -> None:
    now = datetime.now(UTC)
    tenant_a = UUID('00000000-0000-0000-0000-000000000001')
    tenant_b = UUID('00000000-0000-0000-0000-000000000099')
    FakeMarketStore.timeseries = [
        TimeseriesRow(
            id=uuid4(),
            org_id=tenant_a,
            symbol='AAPL',
            timeframe='1day',
            provider='twelvedata',
            ts=now,
            open=200.0,
            high=202.0,
            low=198.5,
            close=201.2,
            volume=1200000,
            fetched_at=now,
        ),
        TimeseriesRow(
            id=uuid4(),
            org_id=tenant_b,
            symbol='AAPL',
            timeframe='1day',
            provider='twelvedata',
            ts=now,
            open=300.0,
            high=305.0,
            low=299.0,
            close=303.2,
            volume=2200000,
            fetched_at=now,
        ),
    ]
    FakeMarketStore.quotes = [
        QuoteRow(
            id=uuid4(),
            org_id=tenant_a,
            symbol='AAPL',
            provider='twelvedata',
            price=201.2,
            change_percent=0.6,
            as_of=now,
            fetched_at=now,
        ),
        QuoteRow(
            id=uuid4(),
            org_id=tenant_b,
            symbol='AAPL',
            provider='twelvedata',
            price=303.2,
            change_percent=1.6,
            as_of=now,
            fetched_at=now,
        ),
    ]

    monkeypatch.setattr('finops_api.routers.market.MarketRepository', FakeMarketRepository)
    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)
        resp_a = client.get(
            '/v1/market/timeseries?symbol=AAPL&limit=5',
            headers={'X-Org-Id': str(tenant_a)},
        )
        assert resp_a.status_code == 200
        assert len(resp_a.json()['data']) == 1
        assert resp_a.json()['data'][0]['open'] == 200.0

        resp_b = client.get(
            '/v1/market/quote?symbol=AAPL',
            headers={'X-Org-Id': str(tenant_b)},
        )
        assert resp_b.status_code == 200
        assert resp_b.json()['data']['price'] == 303.2
    finally:
        app.dependency_overrides.clear()

