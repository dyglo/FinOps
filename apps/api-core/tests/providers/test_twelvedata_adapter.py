from __future__ import annotations

import os

import httpx
import pytest

from finops_api.config import get_settings
from finops_api.providers.base import ProviderError
from finops_api.providers.twelvedata.client import TwelveDataAdapter


def _set_twelvedata_api_key() -> None:
    os.environ['TWELVE_DATA_API_KEY'] = 'test-key'
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_twelvedata_quote_success() -> None:
    _set_twelvedata_api_key()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers['Idempotency-Key'] == 'idem-quote-1'
        return httpx.Response(
            200,
            json={
                'symbol': 'AAPL',
                'close': '189.25',
                'percent_change': '1.1',
                'datetime': '2026-02-09T10:00:00Z',
            },
        )

    adapter = TwelveDataAdapter(transport=httpx.MockTransport(handler))
    response = await adapter.get_quote(
        idempotency_key='idem-quote-1',
        request_payload={'symbol': 'AAPL'},
    )
    assert response.http_status == 200
    assert response.payload['symbol'] == 'AAPL'


@pytest.mark.asyncio
async def test_twelvedata_retries_transient_error() -> None:
    _set_twelvedata_api_key()
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            return httpx.Response(503, json={'status': 'error', 'message': 'busy'})
        return httpx.Response(
            200,
            json={
                'meta': {'symbol': 'AAPL', 'interval': '1day'},
                'values': [],
            },
        )

    adapter = TwelveDataAdapter(transport=httpx.MockTransport(handler), backoff_seconds=0.01)
    await adapter.get_timeseries(
        idempotency_key='idem-ts-1',
        request_payload={'symbol': 'AAPL', 'interval': '1day', 'outputsize': 10},
    )
    assert call_count == 2


@pytest.mark.asyncio
async def test_twelvedata_timeout_exhausts_retries() -> None:
    _set_twelvedata_api_key()

    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout('timeout')

    adapter = TwelveDataAdapter(
        transport=httpx.MockTransport(handler),
        backoff_seconds=0.01,
        max_retries=1,
    )
    with pytest.raises(ProviderError, match='exhausted retries'):
        await adapter.get_quote(
            idempotency_key='idem-quote-2',
            request_payload={'symbol': 'AAPL'},
        )


@pytest.mark.asyncio
async def test_twelvedata_non_retryable_provider_error() -> None:
    _set_twelvedata_api_key()
    call_count = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, json={'status': 'error', 'message': 'invalid symbol'})

    adapter = TwelveDataAdapter(
        transport=httpx.MockTransport(handler),
        backoff_seconds=0.01,
        max_retries=3,
    )
    with pytest.raises(ProviderError, match='exhausted retries'):
        await adapter.get_quote(
            idempotency_key='idem-quote-3',
            request_payload={'symbol': 'INVALID'},
        )
    assert call_count == 1
