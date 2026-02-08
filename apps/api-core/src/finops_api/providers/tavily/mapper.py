from __future__ import annotations

import hashlib
import json

from finops_api.providers.tavily.dto import CanonicalNewsItem, TavilySearchResult


def _stable_document_hash(result: TavilySearchResult) -> str:
    canonical = {
        'url': str(result.url),
        'title': result.title.strip(),
        'content': result.content.strip(),
        'published_date': result.published_date.isoformat() if result.published_date else None,
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def to_canonical_news_item(result: TavilySearchResult) -> CanonicalNewsItem:
    return CanonicalNewsItem(
        source_url=str(result.url),
        title=result.title.strip(),
        snippet=result.content.strip(),
        published_at=result.published_date,
        document_hash=_stable_document_hash(result),
    )