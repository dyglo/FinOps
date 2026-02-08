from __future__ import annotations

import asyncio
from typing import cast

import httpx

from finops_api.config import get_settings
from finops_api.providers.alphavantage.dto import (
    AlphaVantageQuoteRequest,
    AlphaVantageTimeseriesRequest,
)
from finops_api.providers.base import ProviderError, ProviderResponse


class AlphaVantageAdapter:
    def __init__(
        self,
        *,
        base_url: str = 'https://www.alphavantage.co',
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        backoff_seconds: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        if not settings.alpha_vantage_api_key:
            raise ProviderError(
                'ALPHA_VANTAGE_API_KEY is not configured',
                code='provider_config_error',
                provider='alphavantage',
                retryable=False,
            )
        self._api_key = settings.alpha_vantage_api_key
        self._base_url = base_url.rstrip('/')
        self._timeout_seconds = timeout_seconds or settings.provider_timeout_seconds
        self._max_retries = (
            max_retries if max_retries is not None else settings.provider_max_retries
        )
        self._backoff_seconds = backoff_seconds or settings.provider_backoff_seconds
        self._transport = transport

    async def get_quote(
        self,
        *,
        idempotency_key: str,
        request_payload: dict[str, object],
    ) -> ProviderResponse:
        request = AlphaVantageQuoteRequest.model_validate(request_payload)
        payload = await self._get_with_retry(
            idempotency_key=idempotency_key,
            query={
                'function': 'GLOBAL_QUOTE',
                'symbol': request.symbol,
            },
        )
        return ProviderResponse(http_status=200, provider_request_id=None, payload=payload)

    async def get_timeseries(
        self,
        *,
        idempotency_key: str,
        request_payload: dict[str, object],
    ) -> ProviderResponse:
        request = AlphaVantageTimeseriesRequest.model_validate(request_payload)
        if request.interval != '1day':
            raise ProviderError(
                'AlphaVantage currently supports interval=1day for deterministic ingestion',
                code='provider_request_failed',
                provider='alphavantage',
                retryable=False,
            )
        payload = await self._get_with_retry(
            idempotency_key=idempotency_key,
            query={
                'function': 'TIME_SERIES_DAILY',
                'symbol': request.symbol,
                'outputsize': request.outputsize,
            },
        )
        return ProviderResponse(http_status=200, provider_request_id=None, payload=payload)

    async def _get_with_retry(
        self,
        *,
        idempotency_key: str,
        query: dict[str, object],
    ) -> dict[str, object]:
        params = {key: str(value) for key, value in query.items()}
        params['apikey'] = self._api_key
        headers = {'Idempotency-Key': idempotency_key}
        timeout = httpx.Timeout(self._timeout_seconds)
        url = f'{self._base_url}/query'
        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout, transport=self._transport) as client:
                    response = await client.get(url, params=params, headers=headers)
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise ProviderError(
                        f'AlphaVantage transient error: {response.status_code}',
                        code='provider_transient_error',
                        provider='alphavantage',
                        http_status=response.status_code,
                        retryable=True,
                    )
                if response.status_code >= 400:
                    raise ProviderError(
                        f'AlphaVantage request failed: {response.status_code} {response.text}',
                        code='provider_request_failed',
                        provider='alphavantage',
                        http_status=response.status_code,
                        retryable=False,
                    )
                payload = cast(dict[str, object], response.json())
                if payload.get('Error Message') or payload.get('Note'):
                    message = str(payload.get('Error Message') or payload.get('Note'))
                    raise ProviderError(
                        f'AlphaVantage provider error: {message}',
                        code='provider_request_failed',
                        provider='alphavantage',
                        retryable=False,
                    )
                return payload
            except httpx.TimeoutException as exc:
                last_exception = ProviderError(
                    f'AlphaVantage timeout: {exc}',
                    code='provider_timeout',
                    provider='alphavantage',
                    retryable=True,
                )
            except httpx.NetworkError as exc:
                last_exception = ProviderError(
                    f'AlphaVantage network error: {exc}',
                    code='provider_network_error',
                    provider='alphavantage',
                    retryable=True,
                )
            except ProviderError as exc:
                last_exception = exc

            assert last_exception is not None
            if attempt == self._max_retries or not last_exception.retryable:
                break
            await asyncio.sleep(self._backoff_seconds * (2**attempt))

        raise ProviderError(
            f'AlphaVantage request exhausted retries: {last_exception}',
            code='provider_retries_exhausted',
            provider='alphavantage',
            retryable=False,
        )
