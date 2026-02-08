from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.intel import IntelRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.intel import IntelRunCreate, IntelRunRead

router = APIRouter(prefix='/v1/intel', tags=['intel'])


@router.post('/runs', response_model=ApiResponse[IntelRunRead])
async def create_run(
    payload: IntelRunCreate,
    request: Request,
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[IntelRunRead]:
    repo = IntelRepository(session)
    run = await repo.create(org_id=org_id, payload=payload)
    return ApiResponse[IntelRunRead](
        data=IntelRunRead.model_validate(run, from_attributes=True),
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            ts=datetime.now(UTC),
        ),
    )


@router.get('/runs/{run_id}', response_model=ApiResponse[IntelRunRead])
async def get_run(
    run_id: UUID,
    request: Request,
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[IntelRunRead]:
    repo = IntelRepository(session)
    run = await repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Run not found')

    return ApiResponse[IntelRunRead](
        data=IntelRunRead.model_validate(run, from_attributes=True),
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            ts=datetime.now(UTC),
        ),
    )
