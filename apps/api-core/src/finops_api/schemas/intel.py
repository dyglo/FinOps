from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class IntelRunCreate(BaseModel):
    run_type: str = Field(min_length=2, max_length=64)
    model_name: str = Field(min_length=2, max_length=128)
    prompt_version: str = Field(min_length=1, max_length=64)
    input_snapshot_uri: str = Field(min_length=3)
    input_payload: dict[str, Any] = Field(default_factory=dict)
    execution_mode: Literal['live', 'replay'] = 'live'
    replay_source_run_id: UUID | None = None


class IntelRunRead(BaseModel):
    id: UUID
    org_id: UUID
    run_type: str
    status: str
    model_name: str
    prompt_version: str
    input_snapshot_uri: str
    input_payload: dict[str, Any]
    graph_version: str
    execution_mode: str
    replay_source_run_id: UUID | None
    error_message: str | None
    completed_at: datetime | None
    output_payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class IntelReplayCreate(BaseModel):
    model_name: str | None = Field(default=None, min_length=2, max_length=128)
    prompt_version: str | None = Field(default=None, min_length=1, max_length=64)
