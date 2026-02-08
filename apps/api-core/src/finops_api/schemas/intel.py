from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class IntelRunCreate(BaseModel):
    run_type: str = Field(min_length=2, max_length=64)
    model_name: str = Field(min_length=2, max_length=128)
    prompt_version: str = Field(min_length=1, max_length=64)
    input_snapshot_uri: str = Field(min_length=3)


class IntelRunRead(BaseModel):
    id: UUID
    org_id: UUID
    run_type: str
    status: str
    model_name: str
    prompt_version: str
    input_snapshot_uri: str
    output_payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime