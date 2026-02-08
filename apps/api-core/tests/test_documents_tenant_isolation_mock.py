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
class NewsRow:
    id: UUID
    org_id: UUID
    job_id: UUID
    source_provider: str
    normalization_version: str
    source_url: str
    title: str
    snippet: str
    author: str | None
    language: str | None
    published_at: datetime | None
    created_at: datetime


class FakeNewsStore:
    rows: list[NewsRow] = []


class FakeNewsDocumentRepository:
    def __init__(self, session: DummySession) -> None:
        self._session = session

    async def list_news(
        self,
        *,
        org_id: UUID,  # noqa: ARG002
        job_id: UUID | None,
        q: str | None,
        limit: int,
        offset: int,
    ) -> list[NewsRow]:
        rows = [row for row in FakeNewsStore.rows if row.org_id == self._session.org_id]
        if job_id is not None:
            rows = [row for row in rows if row.job_id == job_id]
        if q:
            lowered = q.lower()
            rows = [
                row
                for row in rows
                if lowered in row.title.lower() or lowered in row.snippet.lower()
            ]
        return rows[offset : offset + limit]


async def override_tenant_session(org_id: UUID = Depends(get_org_id)):
    yield DummySession(org_id=org_id)


def test_documents_news_enforces_tenant_isolation(monkeypatch) -> None:
    tenant_a = UUID('00000000-0000-0000-0000-000000000001')
    tenant_b = UUID('00000000-0000-0000-0000-000000000099')
    now = datetime.now(UTC)
    FakeNewsStore.rows = [
        NewsRow(
            id=uuid4(),
            org_id=tenant_a,
            job_id=uuid4(),
            source_provider='tavily',
            normalization_version='v1',
            source_url='https://example.com/org-a',
            title='Org A headline',
            snippet='Only visible to org A',
            author=None,
            language='en',
            published_at=now,
            created_at=now,
        ),
        NewsRow(
            id=uuid4(),
            org_id=tenant_b,
            job_id=uuid4(),
            source_provider='tavily',
            normalization_version='v1',
            source_url='https://example.com/org-b',
            title='Org B headline',
            snippet='Only visible to org B',
            author=None,
            language='en',
            published_at=now,
            created_at=now,
        ),
    ]

    monkeypatch.setattr(
        'finops_api.routers.documents.NewsDocumentRepository',
        FakeNewsDocumentRepository,
    )
    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)
        response_a = client.get(
            '/v1/documents/news',
            headers={'X-Org-Id': str(tenant_a)},
        )
        assert response_a.status_code == 200
        data_a = response_a.json()['data']
        assert len(data_a) == 1
        assert data_a[0]['title'] == 'Org A headline'

        response_b = client.get(
            '/v1/documents/news',
            headers={'X-Org-Id': str(tenant_b)},
        )
        assert response_b.status_code == 200
        data_b = response_b.json()['data']
        assert len(data_b) == 1
        assert data_b[0]['title'] == 'Org B headline'
    finally:
        app.dependency_overrides.clear()
