from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.ingestion import IngestionRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.ingestion import IngestionJobCreate, IngestionJobRead

router = APIRouter(prefix='/v1/ingestion', tags=['ingestion'])


@router.post('/jobs', response_model=ApiResponse[IngestionJobRead])
async def create_job(
    payload: IngestionJobCreate,
    request: Request,
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[IngestionJobRead]:
    repo = IngestionRepository(session)
    job = await repo.create(org_id=org_id, payload=payload)
    return ApiResponse[IngestionJobRead](
        data=IngestionJobRead.model_validate(job, from_attributes=True),
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            ts=datetime.now(UTC),
        ),
    )


@router.get('/jobs/{job_id}', response_model=ApiResponse[IngestionJobRead])
async def get_job(
    job_id: UUID,
    request: Request,
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[IngestionJobRead]:
    repo = IngestionRepository(session)
    job = await repo.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')

    return ApiResponse[IngestionJobRead](
        data=IngestionJobRead.model_validate(job, from_attributes=True),
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            ts=datetime.now(UTC),
        ),
    )
