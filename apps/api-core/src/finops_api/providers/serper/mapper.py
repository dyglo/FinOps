from __future__ import annotations

import hashlib
import json

from finops_api.providers.serper.dto import CanonicalNewsItem, SerperNewsResult


def _stable_document_hash(result: SerperNewsResult) -> str:
    canonical = {
        'url': str(result.link),
        'title': result.title.strip(),
        'snippet': result.snippet.strip(),
        'date': result.date,
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def to_canonical_news_item(result: SerperNewsResult) -> CanonicalNewsItem:
    return CanonicalNewsItem(
        source_provider='serper',
        source_url=str(result.link),
        title=result.title.strip(),
        snippet=result.snippet.strip(),
        author=result.source,
        published_at=result.parsed_date(),
        document_hash=_stable_document_hash(result),
    )
