from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import ToolCallAudit


async def audit_tool_call(
    *,
    session: AsyncSession,
    org_id: UUID,
    run_id: UUID,
    tool_name: str,
    status: str,
    request_payload: dict[str, object],
    response_payload: dict[str, object],
    citations: Sequence[str],
) -> ToolCallAudit:
    audit = ToolCallAudit(
        org_id=org_id,
        run_id=run_id,
        tool_name=tool_name,
        status=status,
        request_payload=request_payload,
        response_payload=response_payload,
        citations=list(citations),
    )
    session.add(audit)
    await session.commit()
    await session.refresh(audit)
    return audit