from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.signals import SignalRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.signals import SignalFeatureRead

router = APIRouter(prefix='/v1/signals', tags=['signals'])


@router.get('/query', response_model=ApiResponse[list[SignalFeatureRead]])
async def query_signals(
    request: Request,
    symbol: str = Query(min_length=1, max_length=16),
    limit: int = Query(default=100, ge=1, le=1000),
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[list[SignalFeatureRead]]:
    repo = SignalRepository(session)
    rows = await repo.query(symbol=symbol, limit=limit)
    return ApiResponse[list[SignalFeatureRead]](
        data=[SignalFeatureRead.model_validate(row, from_attributes=True) for row in rows],
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            ts=datetime.now(UTC),
        ),
    )
