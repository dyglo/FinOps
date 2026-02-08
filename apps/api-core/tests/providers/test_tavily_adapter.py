from __future__ import annotations

import os

import httpx
import pytest

from finops_api.config import get_settings
from finops_api.providers.base import ProviderError
from finops_api.providers.tavily.client import TavilyAdapter


def _set_tavily_api_key() -> None:
    os.environ['TAVILY_API_KEY'] = 'test-key'
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_tavily_adapter_success_returns_typed_payload() -> None:
    _set_tavily_api_key()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers['Idempotency-Key'] == 'idem-1'
        return httpx.Response(
            200,
            json={
                'query': 'nvda',
                'response_time': 0.01,
                'results': [
                    {
                        'title': 'NVIDIA beats estimates',
                        'url': 'https://example.com/news/nvda',
                        'content': 'Revenue grows strongly.',
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    adapter = TavilyAdapter(transport=transport)

    response = await adapter.search_news(
        idempotency_key='idem-1',
        request_payload={'query': 'nvda', 'max_results': 5},
    )

    assert response.http_status == 200
    assert response.payload['query'] == 'nvda'
    assert len(response.payload['results']) == 1


@pytest.mark.asyncio
async def test_tavily_adapter_retries_transient_error() -> None:
    _set_tavily_api_key()
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            return httpx.Response(503, json={'error': 'busy'})
        return httpx.Response(
            200,
            json={
                'query': 'rates',
                'results': [
                    {
                        'title': 'Fed update',
                        'url': 'https://example.com/fed',
                        'content': '...',
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    adapter = TavilyAdapter(transport=transport, backoff_seconds=0.01)

    response = await adapter.search_news(
        idempotency_key='idem-2',
        request_payload={'query': 'rates', 'max_results': 3},
    )

    assert call_count == 2
    assert response.payload['query'] == 'rates'


@pytest.mark.asyncio
async def test_tavily_adapter_timeout_exhausts_retries() -> None:
    _set_tavily_api_key()

    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout('timeout')

    transport = httpx.MockTransport(handler)
    adapter = TavilyAdapter(transport=transport, backoff_seconds=0.01, max_retries=1)

    with pytest.raises(ProviderError, match='exhausted retries'):
        await adapter.search_news(
            idempotency_key='idem-3',
            request_payload={'query': 'macro', 'max_results': 2},
        )


@pytest.mark.asyncio
async def test_tavily_adapter_does_not_retry_non_retryable_4xx() -> None:
    _set_tavily_api_key()
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, json={'error': 'unauthorized'})

    transport = httpx.MockTransport(handler)
    adapter = TavilyAdapter(transport=transport, backoff_seconds=0.01, max_retries=3)

    with pytest.raises(ProviderError, match='exhausted retries'):
        await adapter.search_news(
            idempotency_key='idem-4',
            request_payload={'query': 'macro', 'max_results': 2},
        )

    assert call_count == 1
