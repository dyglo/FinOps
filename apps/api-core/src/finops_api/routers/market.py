from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.market import MarketRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.market import TimeseriesPointRead

router = APIRouter(prefix='/v1/market', tags=['market'])


@router.get('/timeseries', response_model=ApiResponse[list[TimeseriesPointRead]])
async def get_timeseries(
    request: Request,
    symbol: str = Query(min_length=1, max_length=16),
    limit: int = Query(default=100, ge=1, le=1000),
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[list[TimeseriesPointRead]]:
    repo = MarketRepository(session)
    rows = await repo.get_timeseries(symbol=symbol, limit=limit)
    return ApiResponse[list[TimeseriesPointRead]](
        data=[TimeseriesPointRead.model_validate(row, from_attributes=True) for row in rows],
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            ts=datetime.now(UTC),
        ),
    )
