from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import ToolCallAudit


class ToolCallAuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        org_id: UUID,
        run_id: UUID,
        tool_name: str,
        status: str,
        request_payload: dict[str, object],
        response_payload: dict[str, object],
        citations: list[str],
    ) -> ToolCallAudit:
        row = ToolCallAudit(
            org_id=org_id,
            run_id=run_id,
            tool_name=tool_name,
            status=status,
            request_payload=request_payload,
            response_payload=response_payload,
            citations=citations,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def list_by_run_id(self, *, run_id: UUID) -> list[ToolCallAudit]:
        stmt = (
            select(ToolCallAudit)
            .where(ToolCallAudit.run_id == run_id)
            .order_by(ToolCallAudit.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
