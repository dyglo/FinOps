from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import MarketTimeseries


class MarketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_timeseries(self, symbol: str, limit: int) -> list[MarketTimeseries]:
        stmt = (
            select(MarketTimeseries)
            .where(MarketTimeseries.symbol == symbol.upper())
            .order_by(desc(MarketTimeseries.ts))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())