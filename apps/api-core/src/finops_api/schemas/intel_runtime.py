from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class NewsSearchToolInput(BaseModel):
    tool_name: Literal['news_document_search'] = 'news_document_search'
    query: str = Field(min_length=2, max_length=256)
    limit: int = Field(default=5, ge=1, le=20)
    job_id: UUID | None = None


class NewsSearchEvidence(BaseModel):
    title: str
    source_url: str
    snippet: str
    published_at: datetime | None = None
    citations: list[str] = Field(default_factory=list)


class NewsSearchToolOutput(BaseModel):
    tool_name: Literal['news_document_search'] = 'news_document_search'
    documents: list[NewsSearchEvidence] = Field(default_factory=list)


class IntelClaim(BaseModel):
    claim: str
    citations: list[str] = Field(default_factory=list)


class IntelRunOutput(BaseModel):
    graph_version: str = 'v1'
    execution_mode: Literal['live', 'replay']
    summary: str
    claims: list[IntelClaim] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    tool_count: int = 0