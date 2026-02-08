from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.intel import IntelRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.intel import IntelReplayCreate, IntelRunCreate, IntelRunRead
from finops_api.services.intel_runtime import execute_intel_run

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
    try:
        run = await execute_intel_run(session=session, run=run, org_id=org_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Intel run execution failed: {exc}',
        ) from exc

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


@router.post('/runs/{run_id}/replay', response_model=ApiResponse[IntelRunRead])
async def replay_run(
    run_id: UUID,
    request: Request,
    payload: IntelReplayCreate,
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[IntelRunRead]:
    repo = IntelRepository(session)
    source = await repo.get(run_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Source run not found')

    replay_run = await repo.create_replay(org_id=org_id, source_run=source)
    if payload.model_name is not None:
        replay_run.model_name = payload.model_name
    if payload.prompt_version is not None:
        replay_run.prompt_version = payload.prompt_version
    await session.commit()
    await session.refresh(replay_run)

    try:
        replay_run = await execute_intel_run(session=session, run=replay_run, org_id=org_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Intel replay execution failed: {exc}',
        ) from exc

    return ApiResponse[IntelRunRead](
        data=IntelRunRead.model_validate(replay_run, from_attributes=True),
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            ts=datetime.now(UTC),
        ),
    )
