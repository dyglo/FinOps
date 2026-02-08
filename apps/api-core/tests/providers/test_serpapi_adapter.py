from __future__ import annotations

import os

import httpx
import pytest

from finops_api.config import get_settings
from finops_api.providers.base import ProviderError
from finops_api.providers.serpapi.client import SerpApiAdapter


def _set_serpapi_api_key() -> None:
    os.environ['SERPAPI_API_KEY'] = 'test-key'
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_serpapi_adapter_success_returns_typed_payload() -> None:
    _set_serpapi_api_key()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers['Idempotency-Key'] == 'idem-serpapi-1'
        return httpx.Response(
            200,
            json={
                'news_results': [
                    {
                        'title': 'NVIDIA beats estimates',
                        'link': 'https://example.com/news/nvda',
                        'snippet': 'Revenue grows strongly.',
                        'date': '2026-02-08T10:15:00Z',
                        'source': 'ExampleWire',
                    }
                ]
            },
        )

    adapter = SerpApiAdapter(transport=httpx.MockTransport(handler))
    response = await adapter.search_news(
        idempotency_key='idem-serpapi-1',
        request_payload={'query': 'nvidia earnings', 'num': 5},
    )

    assert response.http_status == 200
    assert len(response.payload['news_results']) == 1


@pytest.mark.asyncio
async def test_serpapi_adapter_retries_transient_error() -> None:
    _set_serpapi_api_key()
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            return httpx.Response(503, json={'error': 'busy'})
        return httpx.Response(200, json={'news_results': []})

    adapter = SerpApiAdapter(transport=httpx.MockTransport(handler), backoff_seconds=0.01)
    await adapter.search_news(
        idempotency_key='idem-serpapi-2',
        request_payload={'q': 'rates', 'num': 3},
    )
    assert call_count == 2


@pytest.mark.asyncio
async def test_serpapi_adapter_timeout_exhausts_retries() -> None:
    _set_serpapi_api_key()

    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout('timeout')

    adapter = SerpApiAdapter(
        transport=httpx.MockTransport(handler),
        backoff_seconds=0.01,
        max_retries=1,
    )
    with pytest.raises(ProviderError, match='exhausted retries'):
        await adapter.search_news(
            idempotency_key='idem-serpapi-3',
            request_payload={'q': 'macro', 'num': 2},
        )


@pytest.mark.asyncio
async def test_serpapi_adapter_does_not_retry_non_retryable_4xx() -> None:
    _set_serpapi_api_key()
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, json={'error': 'unauthorized'})

    adapter = SerpApiAdapter(
        transport=httpx.MockTransport(handler),
        backoff_seconds=0.01,
        max_retries=3,
    )
    with pytest.raises(ProviderError, match='exhausted retries'):
        await adapter.search_news(
            idempotency_key='idem-serpapi-4',
            request_payload={'q': 'macro', 'num': 2},
        )
    assert call_count == 1
