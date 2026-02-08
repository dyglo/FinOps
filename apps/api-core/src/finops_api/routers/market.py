from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.dependencies import get_org_id, get_tenant_session
from finops_api.repositories.market import MarketRepository
from finops_api.schemas.common import ApiResponse, MetaEnvelope
from finops_api.schemas.market import MarketQuoteRead, TimeseriesPointRead

router = APIRouter(prefix='/v1/market', tags=['market'])


@router.get('/timeseries', response_model=ApiResponse[list[TimeseriesPointRead]])
async def get_timeseries(
    request: Request,
    symbol: str = Query(min_length=1, max_length=16),
    timeframe: str | None = Query(default=None, min_length=2, max_length=16),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[list[TimeseriesPointRead]]:
    repo = MarketRepository(session)
    rows = await repo.get_timeseries(
        org_id=org_id,
        symbol=symbol,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=limit,
    )
    return ApiResponse[list[TimeseriesPointRead]](
        data=[TimeseriesPointRead.model_validate(row, from_attributes=True) for row in rows],
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            trace_id=request.state.trace_id,
            ts=datetime.now(UTC),
        ),
    )


@router.get('/quote', response_model=ApiResponse[MarketQuoteRead])
async def get_quote(
    request: Request,
    symbol: str = Query(min_length=1, max_length=16),
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_tenant_session),
) -> ApiResponse[MarketQuoteRead]:
    repo = MarketRepository(session)
    row = await repo.get_latest_quote(org_id=org_id, symbol=symbol)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Quote not found')

    return ApiResponse[MarketQuoteRead](
        data=MarketQuoteRead.model_validate(row, from_attributes=True),
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            trace_id=request.state.trace_id,
            ts=datetime.now(UTC),
        ),
    )

