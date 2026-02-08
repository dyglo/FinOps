from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IngestionJobCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'provider': 'tavily',
                'resource': 'news_search',
                'idempotency_key': 'news-nvda-20260208-001',
                'payload': {'query': 'nvidia earnings', 'max_results': 8},
            }
        }
    )

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
    schema_version: str
    attempt_count: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    raw_record_count: int = 0
    normalized_record_count: int = 0
    created_at: datetime
    updated_at: datetime
