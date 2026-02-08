from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from finops_api.dependencies import get_org_id
from finops_api.schemas.common import ApiResponse, MetaEnvelope

router = APIRouter(prefix='/v1/system', tags=['system'])


@router.get('/context', response_model=ApiResponse[dict[str, str]])
async def get_context(
    request: Request,
    org_id: UUID = Depends(get_org_id),
) -> ApiResponse[dict[str, str]]:
    return ApiResponse[dict[str, str]](
        data={'org_id': str(org_id)},
        meta=MetaEnvelope(
            request_id=request.state.request_id,
            org_id=org_id,
            trace_id=request.state.trace_id,
            ts=datetime.now(UTC),
        ),
    )
