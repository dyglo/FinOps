from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator


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

    @field_validator('published_date', mode='before')
    @classmethod
    def parse_published_date(cls, value: object) -> object:
        if value is None or isinstance(value, datetime):
            return value
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return None
            for fmt in (
                '%a, %d %b %Y %H:%M:%S GMT',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%S.%f%z',
                '%Y-%m-%d',
            ):
                try:
                    return datetime.strptime(raw, fmt)
                except ValueError:
                    continue
        return value


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
