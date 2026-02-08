from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.news_documents import NewsDocumentRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.documents import NewsDocumentRead

router = APIRouter(prefix='/v1/documents', tags=['documents'])


@router.get('/news', response_model=ApiResponse[list[NewsDocumentRead]])
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
    rows = await repo.list_news(job_id=job_id, q=q, limit=limit, offset=offset)

    return ApiResponse[list[NewsDocumentRead]](
        data=[NewsDocumentRead.model_validate(row, from_attributes=True) for row in rows],
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            ts=datetime.now(UTC),
        ),
    )