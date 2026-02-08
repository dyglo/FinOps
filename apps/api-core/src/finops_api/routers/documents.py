from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.news_documents import NewsDocumentRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.documents import NewsDocumentRead

LIST_NEWS_EXAMPLE = {
    'data': [
        {
            'id': 'f1572f85-9a36-4a5c-aef1-41172bdb89b4',
            'org_id': '00000000-0000-0000-0000-000000000001',
            'job_id': '3f4b1ea3-0571-4412-a4cf-59b8a70f4481',
            'source_provider': 'tavily',
            'normalization_version': 'v1',
            'source_url': 'https://example.com/nvidia-earnings',
            'title': 'NVIDIA beats expectations in latest quarter',
            'snippet': 'Revenue and guidance both exceeded consensus.',
            'author': None,
            'language': 'en',
            'published_at': '2026-02-08T18:45:00Z',
            'created_at': '2026-02-08T20:12:07.123456Z',
        }
    ],
    'error': None,
    'meta': {
        'request_id': 'db533319-b2f9-47f3-b6f5-a7f3f7b1dc79',
        'org_id': '00000000-0000-0000-0000-000000000001',
        'ts': '2026-02-08T20:12:10.123456Z',
        'version': 'v1',
    },
}

router = APIRouter(prefix='/v1/documents', tags=['documents'])


@router.get(
    '/news',
    response_model=ApiResponse[list[NewsDocumentRead]],
    responses={200: {'content': {'application/json': {'example': LIST_NEWS_EXAMPLE}}}},
)
async def list_news_documents(
    request: Request,
    job_id: UUID | None = Query(default=None),
    q: str | None = Query(default=None, min_length=1, max_length=128),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[list[NewsDocumentRead]]:
    repo = NewsDocumentRepository(session)
    rows = await repo.list_news(org_id=org_id, job_id=job_id, q=q, limit=limit, offset=offset)

    return ApiResponse[list[NewsDocumentRead]](
        data=[NewsDocumentRead.model_validate(row, from_attributes=True) for row in rows],
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            trace_id=request.state.trace_id,
            ts=datetime.now(UTC),
        ),
    )

