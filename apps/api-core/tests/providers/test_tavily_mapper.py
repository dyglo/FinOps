from __future__ import annotations

from datetime import datetime

from finops_api.providers.tavily.dto import TavilySearchResult
from finops_api.providers.tavily.mapper import to_canonical_news_item


def test_tavily_mapper_is_deterministic() -> None:
    result = TavilySearchResult(
        title='Market Wrap',
        url='https://example.com/market-wrap',
        content='Stocks ended mixed.',
        published_date=datetime.fromisoformat('2026-02-08T10:15:00+00:00'),
    )

    item_a = to_canonical_news_item(result)
    item_b = to_canonical_news_item(result)

    assert item_a.document_hash == item_b.document_hash
    assert item_a.source_provider == 'tavily'
    assert item_a.source_url == 'https://example.com/market-wrap'