from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from finops_api.services import intel_runtime


@dataclass
class FakeRun:
    id: UUID
    execution_mode: str
    replay_source_run_id: UUID | None
    input_payload: dict[str, object]
    input_snapshot_uri: str
    status: str = 'pending'
    output_payload: dict[str, object] = field(default_factory=dict)
    error_message: str | None = None
    completed_at: datetime | None = None


class FakeIntelRepository:
    def __init__(self, session: object) -> None:  # noqa: ARG002
        pass

    async def mark_running(self, run: FakeRun) -> FakeRun:
        run.status = 'running'
        return run

    async def mark_completed(self, run: FakeRun, output_payload: dict[str, object]) -> FakeRun:
        run.status = 'completed'
        run.output_payload = output_payload
        run.completed_at = datetime.now(UTC)
        return run

    async def mark_failed(self, run: FakeRun, error_message: str) -> FakeRun:
        run.status = 'failed'
        run.error_message = error_message
        run.completed_at = datetime.now(UTC)
        return run


class FakeToolAuditRepository:
    created_entries: list[dict[str, object]] = []
    source_entries: list[SimpleNamespace] = []

    def __init__(self, session: object) -> None:  # noqa: ARG002
        pass

    async def create(self, **kwargs: object) -> SimpleNamespace:
        self.created_entries.append(kwargs)
        return SimpleNamespace(**kwargs)

    async def list_by_run_id(self, *, run_id: UUID) -> list[SimpleNamespace]:  # noqa: ARG002
        return self.source_entries


class FakeNewsRepository:
    rows: list[SimpleNamespace] = []

    def __init__(self, session: object) -> None:  # noqa: ARG002
        pass

    async def list_news(
        self,
        *,
        job_id: UUID | None,
        q: str | None,
        limit: int,
        offset: int,
    ) -> list[SimpleNamespace]:
        _ = (job_id, q, limit, offset)
        return self.rows


@pytest.mark.asyncio
async def test_execute_intel_run_live_mode_success(monkeypatch) -> None:
    FakeToolAuditRepository.created_entries = []
    FakeNewsRepository.rows = [
        SimpleNamespace(
            title='NVIDIA posts record quarter',
            source_url='https://example.com/nvda',
            snippet='Quarterly growth accelerated.',
            published_at=None,
        )
    ]

    monkeypatch.setattr(intel_runtime, 'IntelRepository', FakeIntelRepository)
    monkeypatch.setattr(intel_runtime, 'ToolCallAuditRepository', FakeToolAuditRepository)
    monkeypatch.setattr(intel_runtime, 'NewsDocumentRepository', FakeNewsRepository)

    run = FakeRun(
        id=uuid4(),
        execution_mode='live',
        replay_source_run_id=None,
        input_payload={'query': 'nvidia', 'limit': 5},
        input_snapshot_uri='nvidia',
    )

    result = await intel_runtime.execute_intel_run(session=object(), run=run, org_id=uuid4())

    assert result.status == 'completed'
    assert result.output_payload['execution_mode'] == 'live'
    assert result.output_payload['tool_count'] == 1
    assert result.output_payload['citations'] == ['https://example.com/nvda']
    assert FakeToolAuditRepository.created_entries[0]['status'] == 'success'


@pytest.mark.asyncio
async def test_execute_intel_run_replay_mode_uses_stored_tool_response(monkeypatch) -> None:
    FakeToolAuditRepository.created_entries = []
    source_run_id = uuid4()
    FakeToolAuditRepository.source_entries = [
        SimpleNamespace(
            tool_name='news_document_search',
            request_payload={
                'tool_name': 'news_document_search',
                'query': 'fed',
                'limit': 3,
                'job_id': None,
            },
            response_payload={
                'tool_name': 'news_document_search',
                'documents': [
                    {
                        'title': 'Fed minutes released',
                        'source_url': 'https://example.com/fed',
                        'snippet': 'Policy outlook remains data dependent.',
                        'published_at': None,
                        'citations': ['https://example.com/fed'],
                    }
                ],
            },
            citations=['https://example.com/fed'],
            created_at=datetime.now(UTC),
        )
    ]

    monkeypatch.setattr(intel_runtime, 'IntelRepository', FakeIntelRepository)
    monkeypatch.setattr(intel_runtime, 'ToolCallAuditRepository', FakeToolAuditRepository)
    monkeypatch.setattr(intel_runtime, 'NewsDocumentRepository', FakeNewsRepository)

    run = FakeRun(
        id=uuid4(),
        execution_mode='replay',
        replay_source_run_id=source_run_id,
        input_payload={'query': 'fed', 'limit': 3},
        input_snapshot_uri='fed',
    )

    result = await intel_runtime.execute_intel_run(session=object(), run=run, org_id=uuid4())

    assert result.status == 'completed'
    assert result.output_payload['execution_mode'] == 'replay'
    assert result.output_payload['citations'] == ['https://example.com/fed']
    assert FakeToolAuditRepository.created_entries[0]['status'] == 'replayed'


@pytest.mark.asyncio
async def test_execute_intel_run_fails_when_claim_has_no_citation(monkeypatch) -> None:
    FakeToolAuditRepository.created_entries = []
    FakeNewsRepository.rows = [
        SimpleNamespace(
            title='No source URL row',
            source_url='',
            snippet='Missing citation should fail.',
            published_at=None,
        )
    ]

    monkeypatch.setattr(intel_runtime, 'IntelRepository', FakeIntelRepository)
    monkeypatch.setattr(intel_runtime, 'ToolCallAuditRepository', FakeToolAuditRepository)
    monkeypatch.setattr(intel_runtime, 'NewsDocumentRepository', FakeNewsRepository)

    run = FakeRun(
        id=uuid4(),
        execution_mode='live',
        replay_source_run_id=None,
        input_payload={'query': 'citation test', 'limit': 5},
        input_snapshot_uri='citation test',
    )

    with pytest.raises(intel_runtime.IntelRuntimeError, match='Citations are required'):
        await intel_runtime.execute_intel_run(session=object(), run=run, org_id=uuid4())

    assert run.status == 'failed'
    assert run.error_message is not None
