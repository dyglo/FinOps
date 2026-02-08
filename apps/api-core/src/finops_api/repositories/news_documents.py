from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, func, or_, select
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

    async def list_by_job(
        self, *, org_id: UUID, job_id: UUID, limit: int = 100
    ) -> list[NewsDocument]:
        stmt = (
            select(NewsDocument)
            .where(NewsDocument.org_id == org_id, NewsDocument.job_id == job_id)
            .order_by(desc(NewsDocument.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_job(self, *, org_id: UUID, job_id: UUID) -> int:
        stmt = select(func.count(NewsDocument.id)).where(
            NewsDocument.org_id == org_id, NewsDocument.job_id == job_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_news(
        self,
        *,
        org_id: UUID,
        job_id: UUID | None,
        q: str | None,
        limit: int,
        offset: int,
    ) -> list[NewsDocument]:
        stmt = select(NewsDocument).where(NewsDocument.org_id == org_id)
        if job_id is not None:
            stmt = stmt.where(NewsDocument.job_id == job_id)
        if q:
            pattern = f'%{q.strip()}%'
            stmt = stmt.where(
                or_(NewsDocument.title.ilike(pattern), NewsDocument.snippet.ilike(pattern))
            )

        stmt = stmt.order_by(desc(NewsDocument.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
