from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import IngestionRawPayload, MarketQuote, MarketTimeseries


class MarketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_timeseries(
        self,
        *,
        org_id: UUID,
        symbol: str,
        timeframe: str | None,
        start: datetime | None,
        end: datetime | None,
        limit: int,
    ) -> list[MarketTimeseries]:
        stmt = (
            select(MarketTimeseries)
            .where(MarketTimeseries.org_id == org_id, MarketTimeseries.symbol == symbol.upper())
            .order_by(desc(MarketTimeseries.ts))
            .limit(limit)
        )
        if timeframe:
            stmt = stmt.where(MarketTimeseries.timeframe == timeframe)
        if start:
            stmt = stmt.where(MarketTimeseries.ts >= start)
        if end:
            stmt = stmt.where(MarketTimeseries.ts <= end)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_quote(self, *, org_id: UUID, symbol: str) -> MarketQuote | None:
        stmt = (
            select(MarketQuote)
            .where(MarketQuote.org_id == org_id, MarketQuote.symbol == symbol.upper())
            .order_by(desc(MarketQuote.as_of))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_timeseries_rows(
        self,
        *,
        org_id: UUID,
        provider: str,
        schema_version: str,
        raw_payload_id: UUID | None,
        rows: list[dict[str, object]],
    ) -> int:
        if not rows:
            return 0

        values = []
        fetched_at = datetime.now(UTC)
        for row in rows:
            values.append(
                {
                    'org_id': org_id,
                    'symbol': str(row['symbol']).upper(),
                    'timeframe': str(row['timeframe']),
                    'provider': provider,
                    'schema_version': schema_version,
                    'raw_payload_id': raw_payload_id,
                    'ts': row['ts'],
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['volume'],
                    'fetched_at': fetched_at,
                }
            )

        stmt = insert(MarketTimeseries).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=['org_id', 'provider', 'symbol', 'timeframe', 'ts'],
            set_={
                'open': stmt.excluded.open,
                'high': stmt.excluded.high,
                'low': stmt.excluded.low,
                'close': stmt.excluded.close,
                'volume': stmt.excluded.volume,
                'raw_payload_id': stmt.excluded.raw_payload_id,
                'fetched_at': stmt.excluded.fetched_at,
            },
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return len(values)

    async def upsert_quote(
        self,
        *,
        org_id: UUID,
        provider: str,
        schema_version: str,
        raw_payload_id: UUID | None,
        symbol: str,
        price: float,
        change_percent: float | None,
        as_of: datetime,
    ) -> MarketQuote:
        insert_stmt = insert(MarketQuote).values(
            org_id=org_id,
            symbol=symbol.upper(),
            provider=provider,
            schema_version=schema_version,
            raw_payload_id=raw_payload_id,
            price=price,
            change_percent=change_percent,
            as_of=as_of,
            fetched_at=datetime.now(UTC),
        )
        update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['org_id', 'provider', 'symbol', 'as_of'],
            set_={
                'price': insert_stmt.excluded.price,
                'change_percent': insert_stmt.excluded.change_percent,
                'raw_payload_id': insert_stmt.excluded.raw_payload_id,
                'fetched_at': insert_stmt.excluded.fetched_at,
            },
        )
        await self.session.execute(update_stmt)
        await self.session.commit()
        latest = await self.get_latest_quote(org_id=org_id, symbol=symbol)
        assert latest is not None
        return latest

    async def count_timeseries_by_job(self, *, org_id: UUID, job_id: UUID) -> int:
        raw_ids_subquery = select(IngestionRawPayload.id).where(
            IngestionRawPayload.org_id == org_id, IngestionRawPayload.job_id == job_id
        )
        stmt = select(func.count(MarketTimeseries.id)).where(
            MarketTimeseries.org_id == org_id,
            MarketTimeseries.raw_payload_id.in_(raw_ids_subquery),
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def count_quotes_by_job(self, *, org_id: UUID, job_id: UUID) -> int:
        raw_ids_subquery = select(IngestionRawPayload.id).where(
            IngestionRawPayload.org_id == org_id, IngestionRawPayload.job_id == job_id
        )
        stmt = select(func.count(MarketQuote.id)).where(
            MarketQuote.org_id == org_id,
            MarketQuote.raw_payload_id.in_(raw_ids_subquery),
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
