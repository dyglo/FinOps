from __future__ import annotations

import os

import httpx
import pytest

from finops_api.config import get_settings
from finops_api.providers.alphavantage.client import AlphaVantageAdapter
from finops_api.providers.base import ProviderError


def _set_alpha_api_key() -> None:
    os.environ['ALPHA_VANTAGE_API_KEY'] = 'test-key'
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_alphavantage_quote_success() -> None:
    _set_alpha_api_key()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers['Idempotency-Key'] == 'idem-av-quote-1'
        return httpx.Response(
            200,
            json={
                'Global Quote': {
                    '01. symbol': 'AAPL',
                    '05. price': '189.25',
                    '07. latest trading day': '2026-02-09',
                }
            },
        )

    adapter = AlphaVantageAdapter(transport=httpx.MockTransport(handler))
    response = await adapter.get_quote(
        idempotency_key='idem-av-quote-1',
        request_payload={'symbol': 'AAPL'},
    )
    assert response.http_status == 200
    assert 'Global Quote' in response.payload


@pytest.mark.asyncio
async def test_alphavantage_retries_transient_error() -> None:
    _set_alpha_api_key()
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            return httpx.Response(503, json={'Note': 'busy'})
        return httpx.Response(
            200,
            json={
                'Meta Data': {'2. Symbol': 'AAPL'},
                'Time Series (Daily)': {},
            },
        )

    adapter = AlphaVantageAdapter(transport=httpx.MockTransport(handler), backoff_seconds=0.01)
    await adapter.get_timeseries(
        idempotency_key='idem-av-ts-1',
        request_payload={'symbol': 'AAPL', 'interval': '1day'},
    )
    assert call_count == 2


@pytest.mark.asyncio
async def test_alphavantage_timeout_exhausts_retries() -> None:
    _set_alpha_api_key()

    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout('timeout')

    adapter = AlphaVantageAdapter(
        transport=httpx.MockTransport(handler),
        backoff_seconds=0.01,
        max_retries=1,
    )
    with pytest.raises(ProviderError, match='exhausted retries'):
        await adapter.get_quote(
            idempotency_key='idem-av-quote-2',
            request_payload={'symbol': 'AAPL'},
        )


@pytest.mark.asyncio
async def test_alphavantage_non_retryable_provider_error() -> None:
    _set_alpha_api_key()
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, json={'Error Message': 'invalid symbol'})

    adapter = AlphaVantageAdapter(
        transport=httpx.MockTransport(handler),
        backoff_seconds=0.01,
        max_retries=3,
    )
    with pytest.raises(ProviderError, match='exhausted retries'):
        await adapter.get_quote(
            idempotency_key='idem-av-quote-3',
            request_payload={'symbol': 'INVALID'},
        )
    assert call_count == 1
