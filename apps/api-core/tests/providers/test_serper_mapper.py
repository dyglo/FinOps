from __future__ import annotations

from finops_api.providers.serper.dto import SerperNewsResult
from finops_api.providers.serper.mapper import to_canonical_news_item


def test_serper_mapper_is_deterministic() -> None:
    result = SerperNewsResult(
        title='Tech stocks rally',
        link='https://example.com/tech-rally',
        snippet='Chip names lead gains.',
        date='2026-02-08T10:15:00Z',
        source='ExampleWire',
    )

    item_a = to_canonical_news_item(result)
    item_b = to_canonical_news_item(result)

    assert item_a.document_hash == item_b.document_hash
    assert item_a.source_provider == 'serper'
    assert item_a.source_url == 'https://example.com/tech-rally'
