from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.ingestion import IngestionRepository
from finops_api.repositories.ingestion_raw_payloads import IngestionRawPayloadRepository
from finops_api.repositories.market import MarketRepository
from finops_api.repositories.news_documents import NewsDocumentRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.ingestion import IngestionJobCreate, IngestionJobRead
from finops_api.services.queue import enqueue_ingestion_job

CREATE_JOB_EXAMPLE = {
    'data': {
        'id': '3f4b1ea3-0571-4412-a4cf-59b8a70f4481',
        'org_id': '00000000-0000-0000-0000-000000000001',
        'provider': 'tavily',
        'resource': 'news_search',
        'status': 'queued',
        'idempotency_key': 'news-nvda-20260208-001',
        'payload': {'query': 'nvidia earnings', 'max_results': 8},
        'schema_version': 'v1',
        'attempt_count': 0,
        'error_message': None,
        'started_at': None,
        'completed_at': None,
        'raw_record_count': 0,
        'normalized_record_count': 0,
        'created_at': '2026-02-08T20:12:00.123456Z',
        'updated_at': '2026-02-08T20:12:00.123456Z',
    },
    'error': None,
    'meta': {
        'request_id': '2afce9f9-7f9f-4bb7-b7bb-e9e11e2c6f2a',
        'org_id': '00000000-0000-0000-0000-000000000001',
        'ts': '2026-02-08T20:12:00.123456Z',
        'version': 'v1',
    },
}

GET_JOB_EXAMPLE = {
    'data': {
        'id': '3f4b1ea3-0571-4412-a4cf-59b8a70f4481',
        'org_id': '00000000-0000-0000-0000-000000000001',
        'provider': 'tavily',
        'resource': 'news_search',
        'status': 'completed',
        'idempotency_key': 'news-nvda-20260208-001',
        'payload': {'query': 'nvidia earnings', 'max_results': 8},
        'schema_version': 'v1',
        'attempt_count': 1,
        'error_message': None,
        'started_at': '2026-02-08T20:12:05.123456Z',
        'completed_at': '2026-02-08T20:12:07.123456Z',
        'raw_record_count': 1,
        'normalized_record_count': 8,
        'created_at': '2026-02-08T20:12:00.123456Z',
        'updated_at': '2026-02-08T20:12:07.123456Z',
    },
    'error': None,
    'meta': {
        'request_id': 'c2660159-a4d8-4ac8-92ad-294683c53033',
        'org_id': '00000000-0000-0000-0000-000000000001',
        'ts': '2026-02-08T20:12:07.123456Z',
        'version': 'v1',
    },
}

router = APIRouter(prefix='/v1/ingestion', tags=['ingestion'])


@router.post(
    '/jobs',
    response_model=ApiResponse[IngestionJobRead],
    responses={200: {'content': {'application/json': {'example': CREATE_JOB_EXAMPLE}}}},
)
async def create_job(
    payload: IngestionJobCreate,
    request: Request,
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[IngestionJobRead]:
    repo = IngestionRepository(session)
    raw_repo = IngestionRawPayloadRepository(session)
    news_repo = NewsDocumentRepository(session)
    market_repo = MarketRepository(session)
    job = await repo.create(org_id=org_id, payload=payload)
    await enqueue_ingestion_job(job_id=job.id, org_id=org_id)
    raw_count = await raw_repo.count_by_job(job_id=job.id)
    normalized_count = await _count_normalized_records(
        org_id=org_id,
        job_id=job.id,
        resource=job.resource,
        news_repo=news_repo,
        market_repo=market_repo,
    )

    data = IngestionJobRead.model_validate(job, from_attributes=True).model_copy(
        update={'raw_record_count': raw_count, 'normalized_record_count': normalized_count}
    )
    return ApiResponse[IngestionJobRead](
        data=data,
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            trace_id=request.state.trace_id,
            ts=datetime.now(UTC),
        ),
    )


@router.get(
    '/jobs/{job_id}',
    response_model=ApiResponse[IngestionJobRead],
    responses={200: {'content': {'application/json': {'example': GET_JOB_EXAMPLE}}}},
)
async def get_job(
    job_id: UUID,
    request: Request,
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[IngestionJobRead]:
    repo = IngestionRepository(session)
    raw_repo = IngestionRawPayloadRepository(session)
    news_repo = NewsDocumentRepository(session)
    market_repo = MarketRepository(session)
    job = await repo.get(org_id=org_id, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')

    raw_count = await raw_repo.count_by_job(job_id=job.id)
    normalized_count = await _count_normalized_records(
        org_id=org_id,
        job_id=job.id,
        resource=job.resource,
        news_repo=news_repo,
        market_repo=market_repo,
    )
    data = IngestionJobRead.model_validate(job, from_attributes=True).model_copy(
        update={'raw_record_count': raw_count, 'normalized_record_count': normalized_count}
    )

    return ApiResponse[IngestionJobRead](
        data=data,
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            trace_id=request.state.trace_id,
            ts=datetime.now(UTC),
        ),
    )


async def _count_normalized_records(
    *,
    org_id: UUID,
    job_id: UUID,
    resource: str,
    news_repo: NewsDocumentRepository,
    market_repo: MarketRepository,
) -> int:
    if resource == 'news_search':
        return await news_repo.count_by_job(org_id=org_id, job_id=job_id)
    if resource == 'market_timeseries_backfill':
        return await market_repo.count_timeseries_by_job(org_id=org_id, job_id=job_id)
    if resource == 'market_quote_refresh':
        return await market_repo.count_quotes_by_job(org_id=org_id, job_id=job_id)
    return 0

