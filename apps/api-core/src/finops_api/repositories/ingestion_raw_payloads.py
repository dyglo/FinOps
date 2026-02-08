from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import IngestionRawPayload


class IngestionRawPayloadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        org_id: UUID,
        job_id: UUID,
        provider: str,
        resource: str,
        content_hash: str,
        request_payload: dict[str, object],
        response_payload: dict[str, object],
        http_status: int | None,
        provider_request_id: str | None,
    ) -> IngestionRawPayload:
        row = IngestionRawPayload(
            org_id=org_id,
            job_id=job_id,
            provider=provider,
            resource=resource,
            schema_version='v1',
            content_hash=content_hash,
            request_payload=request_payload,
            response_payload=response_payload,
            http_status=http_status,
            provider_request_id=provider_request_id,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def get(self, raw_payload_id: UUID) -> IngestionRawPayload | None:
        stmt = select(IngestionRawPayload).where(IngestionRawPayload.id == raw_payload_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_job(self, *, job_id: UUID) -> int:
        stmt = select(func.count(IngestionRawPayload.id)).where(
            IngestionRawPayload.job_id == job_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
