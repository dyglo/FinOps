from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class IngestionJobCreate(BaseModel):
    provider: str = Field(min_length=2, max_length=64)
    resource: str = Field(min_length=2, max_length=128)
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
    created_at: datetime
    updated_at: datetime