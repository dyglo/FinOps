from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NewsDocumentRead(BaseModel):
    id: UUID
    org_id: UUID
    job_id: UUID
    source_provider: str
    normalization_version: str
    source_url: str
    title: str
    snippet: str
    author: str | None
    language: str | None
    published_at: datetime | None
    created_at: datetime
