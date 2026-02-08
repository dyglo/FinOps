from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class TavilySearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=512)
    max_results: int = Field(default=10, ge=1, le=20)
    search_depth: str = Field(default='advanced', pattern='^(basic|advanced)$')
    topic: str = Field(default='news', pattern='^(general|news)$')
    include_raw_content: bool = Field(default=False)


class TavilySearchResult(BaseModel):
    title: str
    url: HttpUrl
    content: str = ''
    score: float | None = None
    published_date: datetime | None = None


class TavilySearchResponse(BaseModel):
    query: str
    response_time: float | None = None
    results: list[TavilySearchResult] = Field(default_factory=list)


class CanonicalNewsItem(BaseModel):
    source_provider: str = 'tavily'
    source_url: str
    title: str
    snippet: str
    author: str | None = None
    language: str | None = None
    published_at: datetime | None = None
    document_hash: str