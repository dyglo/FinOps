from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import IngestionJob
from finops_api.schemas.ingestion import IngestionJobCreate


class IngestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: UUID, payload: IngestionJobCreate) -> IngestionJob:
        existing = await self.get_by_idempotency(
            org_id=org_id,
            provider=payload.provider,
            resource=payload.resource,
            idempotency_key=payload.idempotency_key,
        )
        if existing is not None:
            return existing

        job = IngestionJob(
            org_id=org_id,
            provider=payload.provider,
            resource=payload.resource,
            idempotency_key=payload.idempotency_key,
            payload=payload.payload,
            schema_version='v1',
            status='queued',
            attempt_count=0,
        )
        self.session.add(job)
        try:
            await self.session.commit()
            await self.session.refresh(job)
            return job
        except IntegrityError:
            await self.session.rollback()
            existing = await self.get_by_idempotency(
                org_id=org_id,
                provider=payload.provider,
                resource=payload.resource,
                idempotency_key=payload.idempotency_key,
            )
            if existing is None:
                raise
            return existing

    async def get(self, *, org_id: UUID, job_id: UUID) -> IngestionJob | None:
        stmt = select(IngestionJob).where(
            IngestionJob.org_id == org_id,
            IngestionJob.id == job_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_idempotency(
        self,
        *,
        org_id: UUID,
        provider: str,
        resource: str,
        idempotency_key: str,
    ) -> IngestionJob | None:
        stmt = select(IngestionJob).where(
            IngestionJob.org_id == org_id,
            IngestionJob.provider == provider,
            IngestionJob.resource == resource,
            IngestionJob.idempotency_key == idempotency_key,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_running(self, job: IngestionJob) -> IngestionJob:
        job.status = 'running'
        job.attempt_count += 1
        job.error_message = None
        job.started_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def mark_completed(self, job: IngestionJob) -> IngestionJob:
        job.status = 'completed'
        job.completed_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def mark_failed(self, job: IngestionJob, error_message: str) -> IngestionJob:
        job.status = 'failed'
        job.error_message = error_message[:2048]
        job.completed_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(job)
        return job
