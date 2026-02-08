from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import NewsDocument


class NewsDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_many(self, rows: list[NewsDocument]) -> list[NewsDocument]:
        self.session.add_all(rows)
        await self.session.commit()
        for row in rows:
            await self.session.refresh(row)
        return rows

    async def list_by_job(self, *, job_id: UUID, limit: int = 100) -> list[NewsDocument]:
        stmt = (
            select(NewsDocument)
            .where(NewsDocument.job_id == job_id)
            .order_by(desc(NewsDocument.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
