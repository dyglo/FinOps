from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MetaEnvelope(BaseModel):
    request_id: str
    org_id: UUID
    trace_id: str | None = None
    ts: datetime
    version: str = 'v1'


class ApiResponse[T](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: T
    error: str | None = None
    meta: MetaEnvelope


class Pagination(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
