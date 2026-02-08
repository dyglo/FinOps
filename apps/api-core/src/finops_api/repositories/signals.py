from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import SignalFeature


class SignalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query(self, symbol: str, limit: int) -> list[SignalFeature]:
        stmt = (
            select(SignalFeature)
            .where(SignalFeature.symbol == symbol.upper())
            .order_by(desc(SignalFeature.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())