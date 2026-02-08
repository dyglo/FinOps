from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, model_validator


class SerperSearchRequest(BaseModel):
    q: str = Field(min_length=2, max_length=512)
    num: int = Field(default=10, ge=1, le=20)

    @model_validator(mode='before')
    @classmethod
    def normalize_query_alias(cls, data: object) -> object:
        if isinstance(data, dict) and 'q' not in data and 'query' in data:
            cloned = dict(data)
            cloned['q'] = cloned.pop('query')
            return cloned
        return data


class SerperNewsResult(BaseModel):
    title: str
    link: HttpUrl
    snippet: str = ''
    date: str | None = None
    source: str | None = None

    def parsed_date(self) -> datetime | None:
        if not self.date:
            return None
        try:
            return datetime.fromisoformat(self.date.replace('Z', '+00:00'))
        except ValueError:
            return None


class SerperNewsResponse(BaseModel):
    news: list[SerperNewsResult] = Field(default_factory=list)


class CanonicalNewsItem(BaseModel):
    source_provider: str = 'serper'
    source_url: str
    title: str
    snippet: str
    author: str | None = None
    language: str | None = None
    published_at: datetime | None = None
    document_hash: str
