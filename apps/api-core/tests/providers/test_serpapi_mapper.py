from __future__ import annotations

from finops_api.providers.serpapi.dto import SerpApiNewsResult
from finops_api.providers.serpapi.mapper import to_canonical_news_item


def test_serpapi_mapper_is_deterministic() -> None:
    result = SerpApiNewsResult(
        title='Macro outlook update',
        link='https://example.com/macro-outlook',
        snippet='Rates expectations shift higher.',
        date='2026-02-08T12:00:00Z',
        source='ExampleWire',
    )

    item_a = to_canonical_news_item(result)
    item_b = to_canonical_news_item(result)

    assert item_a.document_hash == item_b.document_hash
    assert item_a.source_provider == 'serpapi'
    assert item_a.source_url == 'https://example.com/macro-outlook'
