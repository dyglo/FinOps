from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import IngestionJob
from finops_api.schemas.ingestion import IngestionJobCreate


class IngestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: UUID, payload: IngestionJobCreate) -> IngestionJob:
        job = IngestionJob(
            org_id=org_id,
            provider=payload.provider,
            resource=payload.resource,
            idempotency_key=payload.idempotency_key,
            payload=payload.payload,
            status='queued',
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get(self, job_id: UUID) -> IngestionJob | None:
        stmt = select(IngestionJob).where(IngestionJob.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()