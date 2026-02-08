from __future__ import annotations

from datetime import UTC, datetime
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
            input_payload=payload.input_payload,
            graph_version='v1',
            execution_mode=payload.execution_mode,
            replay_source_run_id=payload.replay_source_run_id,
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

    async def mark_running(self, run: IntelRun) -> IntelRun:
        run.status = 'running'
        run.error_message = None
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def mark_completed(self, run: IntelRun, output_payload: dict[str, object]) -> IntelRun:
        run.status = 'completed'
        run.output_payload = output_payload
        run.completed_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def mark_failed(self, run: IntelRun, error_message: str) -> IntelRun:
        run.status = 'failed'
        run.error_message = error_message[:2048]
        run.completed_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(run)
        return run
