from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi import Depends
from fastapi.testclient import TestClient

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.main import app


@dataclass
class DummySession:
    org_id: UUID


@dataclass
class JobRecord:
    id: UUID
    org_id: UUID
    provider: str
    resource: str
    status: str
    idempotency_key: str
    payload: dict[str, object]
    schema_version: str
    attempt_count: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class InMemoryStore:
    jobs: dict[UUID, JobRecord] = {}
    raw_counts: dict[UUID, int] = {}
    news_counts: dict[UUID, int] = {}
    market_timeseries_counts: dict[UUID, int] = {}
    market_quote_counts: dict[UUID, int] = {}


class FakeIngestionRepository:
    def __init__(self, session: DummySession) -> None:
        self.session = session

    async def create(self, org_id: UUID, payload: SimpleNamespace) -> JobRecord:
        for job in InMemoryStore.jobs.values():
            if (
                job.org_id == org_id
                and job.provider == payload.provider
                and job.resource == payload.resource
                and job.idempotency_key == payload.idempotency_key
            ):
                return job

        now = datetime.now(UTC)
        job = JobRecord(
            id=uuid4(),
            org_id=org_id,
            provider=payload.provider,
            resource=payload.resource,
            status='queued',
            idempotency_key=payload.idempotency_key,
            payload=payload.payload,
            schema_version='v1',
            attempt_count=0,
            error_message=None,
            started_at=None,
            completed_at=None,
            created_at=now,
            updated_at=now,
        )
        InMemoryStore.jobs[job.id] = job
        return job

    async def get(self, *, org_id: UUID, job_id: UUID) -> JobRecord | None:
        job = InMemoryStore.jobs.get(job_id)
        if job is None:
            return None
        if job.org_id != self.session.org_id or job.org_id != org_id:
            return None
        return job


class FakeIngestionRawPayloadRepository:
    def __init__(self, session: DummySession) -> None:  # noqa: ARG002
        pass

    async def count_by_job(self, *, job_id: UUID) -> int:
        return InMemoryStore.raw_counts.get(job_id, 0)


class FakeNewsDocumentRepository:
    def __init__(self, session: DummySession) -> None:  # noqa: ARG002
        pass

    async def count_by_job(self, *, org_id: UUID, job_id: UUID) -> int:  # noqa: ARG002
        return InMemoryStore.news_counts.get(job_id, 0)


class FakeMarketRepository:
    def __init__(self, session: DummySession) -> None:  # noqa: ARG002
        pass

    async def count_timeseries_by_job(self, *, org_id: UUID, job_id: UUID) -> int:  # noqa: ARG002
        return InMemoryStore.market_timeseries_counts.get(job_id, 0)

    async def count_quotes_by_job(self, *, org_id: UUID, job_id: UUID) -> int:  # noqa: ARG002
        return InMemoryStore.market_quote_counts.get(job_id, 0)


async def fake_enqueue_ingestion_job(*, job_id: UUID, org_id: UUID) -> None:  # noqa: ARG001
    job = InMemoryStore.jobs[job_id]
    job.status = 'completed'
    job.attempt_count = 1
    job.started_at = datetime.now(UTC)
    job.completed_at = datetime.now(UTC)
    job.updated_at = datetime.now(UTC)
    InMemoryStore.raw_counts[job_id] = 1
    if job.resource == 'news_search':
        InMemoryStore.news_counts[job_id] = 2
    elif job.resource == 'market_timeseries_backfill':
        InMemoryStore.market_timeseries_counts[job_id] = 30
    elif job.resource == 'market_quote_refresh':
        InMemoryStore.market_quote_counts[job_id] = 1


async def override_tenant_session(org_id: UUID = Depends(get_org_id)):
    yield DummySession(org_id=org_id)


def test_ingestion_post_then_get_with_mocked_provider(monkeypatch) -> None:
    InMemoryStore.jobs.clear()
    InMemoryStore.raw_counts.clear()
    InMemoryStore.news_counts.clear()
    InMemoryStore.market_timeseries_counts.clear()
    InMemoryStore.market_quote_counts.clear()

    monkeypatch.setattr('finops_api.routers.ingestion.IngestionRepository', FakeIngestionRepository)
    monkeypatch.setattr(
        'finops_api.routers.ingestion.IngestionRawPayloadRepository',
        FakeIngestionRawPayloadRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.NewsDocumentRepository',
        FakeNewsDocumentRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.MarketRepository',
        FakeMarketRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.enqueue_ingestion_job',
        fake_enqueue_ingestion_job,
    )

    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)
        headers = {'X-Org-Id': '00000000-0000-0000-0000-000000000001'}

        create_resp = client.post(
            '/v1/ingestion/jobs',
            headers=headers,
            json={
                'provider': 'tavily',
                'resource': 'news_search',
                'idempotency_key': 'idem-news-1',
                'payload': {'query': 'nvidia earnings', 'max_results': 3},
            },
        )
        assert create_resp.status_code == 200
        job = create_resp.json()['data']
        assert job['status'] == 'completed'
        assert job['schema_version'] == 'v1'
        assert job['attempt_count'] == 1
        assert job['started_at'] is not None
        assert job['completed_at'] is not None
        assert job['raw_record_count'] == 1
        assert job['normalized_record_count'] == 2

        get_resp = client.get(f"/v1/ingestion/jobs/{job['id']}", headers=headers)
        assert get_resp.status_code == 200
        loaded = get_resp.json()['data']
        assert loaded['id'] == job['id']
        assert loaded['status'] == 'completed'
        assert loaded['schema_version'] == 'v1'
        assert loaded['attempt_count'] == 1
        assert loaded['raw_record_count'] == 1
        assert loaded['normalized_record_count'] == 2
    finally:
        app.dependency_overrides.clear()


def test_ingestion_post_then_get_with_serper_provider(monkeypatch) -> None:
    InMemoryStore.jobs.clear()
    InMemoryStore.raw_counts.clear()
    InMemoryStore.news_counts.clear()
    InMemoryStore.market_timeseries_counts.clear()
    InMemoryStore.market_quote_counts.clear()

    monkeypatch.setattr('finops_api.routers.ingestion.IngestionRepository', FakeIngestionRepository)
    monkeypatch.setattr(
        'finops_api.routers.ingestion.IngestionRawPayloadRepository',
        FakeIngestionRawPayloadRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.NewsDocumentRepository',
        FakeNewsDocumentRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.MarketRepository',
        FakeMarketRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.enqueue_ingestion_job',
        fake_enqueue_ingestion_job,
    )

    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)
        headers = {'X-Org-Id': '00000000-0000-0000-0000-000000000001'}

        create_resp = client.post(
            '/v1/ingestion/jobs',
            headers=headers,
            json={
                'provider': 'serper',
                'resource': 'news_search',
                'idempotency_key': 'idem-news-serper-1',
                'payload': {'query': 'nvidia earnings', 'num': 3},
            },
        )
        assert create_resp.status_code == 200
        job = create_resp.json()['data']
        assert job['provider'] == 'serper'
        assert job['status'] == 'completed'
        assert job['raw_record_count'] == 1
        assert job['normalized_record_count'] == 2

        get_resp = client.get(f"/v1/ingestion/jobs/{job['id']}", headers=headers)
        assert get_resp.status_code == 200
        loaded = get_resp.json()['data']
        assert loaded['provider'] == 'serper'
        assert loaded['status'] == 'completed'
    finally:
        app.dependency_overrides.clear()


def test_ingestion_post_then_get_with_serpapi_provider(monkeypatch) -> None:
    InMemoryStore.jobs.clear()
    InMemoryStore.raw_counts.clear()
    InMemoryStore.news_counts.clear()
    InMemoryStore.market_timeseries_counts.clear()
    InMemoryStore.market_quote_counts.clear()

    monkeypatch.setattr('finops_api.routers.ingestion.IngestionRepository', FakeIngestionRepository)
    monkeypatch.setattr(
        'finops_api.routers.ingestion.IngestionRawPayloadRepository',
        FakeIngestionRawPayloadRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.NewsDocumentRepository',
        FakeNewsDocumentRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.MarketRepository',
        FakeMarketRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.enqueue_ingestion_job',
        fake_enqueue_ingestion_job,
    )

    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)
        headers = {'X-Org-Id': '00000000-0000-0000-0000-000000000001'}

        create_resp = client.post(
            '/v1/ingestion/jobs',
            headers=headers,
            json={
                'provider': 'serpapi',
                'resource': 'news_search',
                'idempotency_key': 'idem-news-serpapi-1',
                'payload': {'query': 'nvidia earnings', 'num': 3},
            },
        )
        assert create_resp.status_code == 200
        job = create_resp.json()['data']
        assert job['provider'] == 'serpapi'
        assert job['status'] == 'completed'
        assert job['raw_record_count'] == 1
        assert job['normalized_record_count'] == 2

        get_resp = client.get(f"/v1/ingestion/jobs/{job['id']}", headers=headers)
        assert get_resp.status_code == 200
        loaded = get_resp.json()['data']
        assert loaded['provider'] == 'serpapi'
        assert loaded['status'] == 'completed'
    finally:
        app.dependency_overrides.clear()


def test_ingestion_get_enforces_tenant_isolation(monkeypatch) -> None:
    InMemoryStore.jobs.clear()
    InMemoryStore.raw_counts.clear()
    InMemoryStore.news_counts.clear()
    InMemoryStore.market_timeseries_counts.clear()
    InMemoryStore.market_quote_counts.clear()

    monkeypatch.setattr('finops_api.routers.ingestion.IngestionRepository', FakeIngestionRepository)
    monkeypatch.setattr(
        'finops_api.routers.ingestion.IngestionRawPayloadRepository',
        FakeIngestionRawPayloadRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.NewsDocumentRepository',
        FakeNewsDocumentRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.MarketRepository',
        FakeMarketRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.enqueue_ingestion_job',
        fake_enqueue_ingestion_job,
    )

    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)

        create_resp = client.post(
            '/v1/ingestion/jobs',
            headers={'X-Org-Id': '00000000-0000-0000-0000-000000000001'},
            json={
                'provider': 'tavily',
                'resource': 'news_search',
                'idempotency_key': 'idem-news-2',
                'payload': {'query': 'fed', 'max_results': 2},
            },
        )
        assert create_resp.status_code == 200
        job_id = create_resp.json()['data']['id']

        foreign_resp = client.get(
            f'/v1/ingestion/jobs/{job_id}',
            headers={'X-Org-Id': '00000000-0000-0000-0000-000000000099'},
        )
        assert foreign_resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_ingestion_market_timeseries_job_counts(monkeypatch) -> None:
    InMemoryStore.jobs.clear()
    InMemoryStore.raw_counts.clear()
    InMemoryStore.news_counts.clear()
    InMemoryStore.market_timeseries_counts.clear()
    InMemoryStore.market_quote_counts.clear()

    monkeypatch.setattr('finops_api.routers.ingestion.IngestionRepository', FakeIngestionRepository)
    monkeypatch.setattr(
        'finops_api.routers.ingestion.IngestionRawPayloadRepository',
        FakeIngestionRawPayloadRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.NewsDocumentRepository',
        FakeNewsDocumentRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.MarketRepository',
        FakeMarketRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.enqueue_ingestion_job',
        fake_enqueue_ingestion_job,
    )

    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)
        headers = {'X-Org-Id': '00000000-0000-0000-0000-000000000001'}
        create_resp = client.post(
            '/v1/ingestion/jobs',
            headers=headers,
            json={
                'provider': 'twelvedata',
                'resource': 'market_timeseries_backfill',
                'idempotency_key': 'idem-market-1',
                'payload': {'symbol': 'AAPL', 'interval': '1day', 'outputsize': 30},
            },
        )
        assert create_resp.status_code == 200
        data = create_resp.json()['data']
        assert data['provider'] == 'twelvedata'
        assert data['normalized_record_count'] == 30
    finally:
        app.dependency_overrides.clear()


def test_ingestion_market_quote_job_counts_for_alphavantage(monkeypatch) -> None:
    InMemoryStore.jobs.clear()
    InMemoryStore.raw_counts.clear()
    InMemoryStore.news_counts.clear()
    InMemoryStore.market_timeseries_counts.clear()
    InMemoryStore.market_quote_counts.clear()

    monkeypatch.setattr('finops_api.routers.ingestion.IngestionRepository', FakeIngestionRepository)
    monkeypatch.setattr(
        'finops_api.routers.ingestion.IngestionRawPayloadRepository',
        FakeIngestionRawPayloadRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.NewsDocumentRepository',
        FakeNewsDocumentRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.MarketRepository',
        FakeMarketRepository,
    )
    monkeypatch.setattr(
        'finops_api.routers.ingestion.enqueue_ingestion_job',
        fake_enqueue_ingestion_job,
    )

    app.dependency_overrides[get_tenant_session] = override_tenant_session
    try:
        client = TestClient(app)
        headers = {'X-Org-Id': '00000000-0000-0000-0000-000000000001'}
        create_resp = client.post(
            '/v1/ingestion/jobs',
            headers=headers,
            json={
                'provider': 'alphavantage',
                'resource': 'market_quote_refresh',
                'idempotency_key': 'idem-market-quote-av-1',
                'payload': {'symbol': 'AAPL'},
            },
        )
        assert create_resp.status_code == 200
        data = create_resp.json()['data']
        assert data['provider'] == 'alphavantage'
        assert data['normalized_record_count'] == 1
    finally:
        app.dependency_overrides.clear()
