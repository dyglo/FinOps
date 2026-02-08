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
class SignalRow:
    id: UUID
    org_id: UUID
    symbol: str
    feature_name: str
    feature_version: str
    value: float
    meta: dict[str, object]
    created_at: datetime
    updated_at: datetime


class FakeSignalStore:
    rows: list[SignalRow] = []


class FakeSignalRepository:
    def __init__(self, session: DummySession) -> None:
        self._session = session

    async def query(self, *, org_id: UUID, symbol: str, limit: int) -> list[SignalRow]:
        rows = [
            row
            for row in FakeSignalStore.rows
            if row.org_id == org_id and row.org_id == self._session.org_id and row.symbol == symbol
        ]
        return rows[:limit]


async def override_tenant_session(org_id: UUID = Depends(get_org_id)):
    yield DummySession(org_id=org_id)


def test_signals_query_enforces_tenant_isolation(monkeypatch) -> None:
    now = datetime.now(UTC)
    tenant_a = UUID('00000000-0000-0000-0000-000000000001')
    tenant_b = UUID('00000000-0000-0000-0000-000000000099')
    FakeSignalStore.rows = [
        SignalRow(
            id=uuid4(),
            org_id=tenant_a,
            symbol='AAPL',
            feature_name='news_sentiment_mean',
            feature_version='v1',
            value=0.62,
            meta={'source': 'unit-test'},
            created_at=now,
            updated_at=now,
        ),
        SignalRow(
            id=uuid4(),
            org_id=tenant_b,
            symbol='AAPL',
            feature_name='news_sentiment_mean',
            feature_version='v1',
            value=-0.31,
            meta={'source': 'unit-test'},
            created_at=now,
            updated_at=now,
        ),
    ]

    monkeypatch.setattr('finops_api.routers.signals.SignalRepository', FakeSignalRepository)
    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)
        resp_a = client.get(
            '/v1/signals/query?symbol=AAPL&limit=5',
            headers={'X-Org-Id': str(tenant_a)},
        )
        assert resp_a.status_code == 200
        assert len(resp_a.json()['data']) == 1
        assert resp_a.json()['data'][0]['value'] == 0.62
    finally:
        app.dependency_overrides.clear()

