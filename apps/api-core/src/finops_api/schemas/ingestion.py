from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class IngestionJobCreate(BaseModel):
    provider: Literal['tavily']
    resource: Literal['news_search']
    idempotency_key: str = Field(min_length=4, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)


class IngestionJobRead(BaseModel):
    id: UUID
    org_id: UUID
    provider: str
    resource: str
    status: str
    idempotency_key: str
    payload: dict[str, Any]
    attempt_count: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    raw_record_count: int = 0
    normalized_record_count: int = 0
    created_at: datetime
    updated_at: datetime
