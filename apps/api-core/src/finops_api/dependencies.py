from __future__ import annotations

from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.db import get_db_session


async def get_org_id(x_org_id: str = Header(alias='X-Org-Id')) -> UUID:
    try:
        return UUID(x_org_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid X-Org-Id header. Expected UUID.',
        ) from exc


async def get_tenant_session(
    org_id: UUID = Depends(get_org_id),
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AsyncSession, None]:
    await session.execute(
        text("SELECT set_config('app.current_org_id', :org_id, false)"),
        {'org_id': str(org_id)},
    )
    yield session
