from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import IntelRun
from finops_api.schemas.intel import IntelRunCreate


class IntelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: UUID, payload: IntelRunCreate) -> IntelRun:
        run = IntelRun(
            org_id=org_id,
            run_type=payload.run_type,
            status='pending',
            model_name=payload.model_name,
            prompt_version=payload.prompt_version,
            input_snapshot_uri=payload.input_snapshot_uri,
            output_payload={},
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get(self, run_id: UUID) -> IntelRun | None:
        stmt = select(IntelRun).where(IntelRun.id == run_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()