from __future__ import annotations

import asyncio
from typing import cast

import httpx

from finops_api.config import get_settings
from finops_api.providers.base import ProviderError, ProviderResponse
from finops_api.providers.twelvedata.dto import TwelveDataQuoteRequest, TwelveDataTimeseriesRequest


class TwelveDataAdapter:
    def __init__(
        self,
        *,
        base_url: str = 'https://api.twelvedata.com',
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        backoff_seconds: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        if not settings.twelve_data_api_key:
            raise ProviderError(
                'TWELVE_DATA_API_KEY is not configured',
                code='provider_config_error',
                provider='twelvedata',
                retryable=False,
            )
        self._api_key = settings.twelve_data_api_key
        self._base_url = base_url.rstrip('/')
        self._timeout_seconds = timeout_seconds or settings.provider_timeout_seconds
        self._max_retries = (
            max_retries if max_retries is not None else settings.provider_max_retries
        )
        self._backoff_seconds = backoff_seconds or settings.provider_backoff_seconds
        if self._max_retries < 0:
            raise ProviderError(
                'PROVIDER_MAX_RETRIES must be non-negative',
                code='provider_config_error',
                provider='twelvedata',
                retryable=False,
            )
        self._transport = transport

    async def get_quote(
        self,
        *,
        idempotency_key: str,
        request_payload: dict[str, object],
    ) -> ProviderResponse:
        request = TwelveDataQuoteRequest.model_validate(request_payload)
        payload = await self._get_with_retry(
            path='/quote',
            idempotency_key=idempotency_key,
            query={'symbol': request.symbol},
        )
        return ProviderResponse(http_status=200, provider_request_id=None, payload=payload)

    async def get_timeseries(
        self,
        *,
        idempotency_key: str,
        request_payload: dict[str, object],
    ) -> ProviderResponse:
        request = TwelveDataTimeseriesRequest.model_validate(request_payload)
        query: dict[str, object] = {
            'symbol': request.symbol,
            'interval': request.interval,
            'outputsize': request.outputsize,
        }
        if request.start_date:
            query['start_date'] = request.start_date
        if request.end_date:
            query['end_date'] = request.end_date

        payload = await self._get_with_retry(
            path='/time_series',
            idempotency_key=idempotency_key,
            query=query,
        )
        return ProviderResponse(http_status=200, provider_request_id=None, payload=payload)

    async def _get_with_retry(
        self,
        *,
        path: str,
        idempotency_key: str,
        query: dict[str, object],
    ) -> dict[str, object]:
        params = {key: str(value) for key, value in query.items()}
        params['apikey'] = self._api_key

        headers = {'Idempotency-Key': idempotency_key}
        timeout = httpx.Timeout(self._timeout_seconds)
        url = f'{self._base_url}{path}'
        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout, transport=self._transport) as client:
                    response = await client.get(url, params=params, headers=headers)

                if response.status_code in {429, 500, 502, 503, 504}:
                    raise ProviderError(
                        f'TwelveData transient error: {response.status_code}',
                        code='provider_transient_error',
                        provider='twelvedata',
                        http_status=response.status_code,
                        retryable=True,
                    )
                if response.status_code >= 400:
                    raise ProviderError(
                        f'TwelveData request failed: {response.status_code} {response.text}',
                        code='provider_request_failed',
                        provider='twelvedata',
                        http_status=response.status_code,
                        retryable=False,
                    )

                parsed = cast(dict[str, object], response.json())
                status = str(parsed.get('status', 'ok')).lower()
                if status == 'error':
                    message = str(parsed.get('message', 'unknown error'))
                    raise ProviderError(
                        f'TwelveData provider error: {message}',
                        code='provider_request_failed',
                        provider='twelvedata',
                        retryable=False,
                    )
                return parsed
            except httpx.TimeoutException as exc:
                last_exception = ProviderError(
                    f'TwelveData timeout: {exc}',
                    code='provider_timeout',
                    provider='twelvedata',
                    retryable=True,
                )
            except httpx.NetworkError as exc:
                last_exception = ProviderError(
                    f'TwelveData network error: {exc}',
                    code='provider_network_error',
                    provider='twelvedata',
                    retryable=True,
                )
            except ProviderError as exc:
                last_exception = exc

            assert last_exception is not None
            if attempt == self._max_retries or not last_exception.retryable:
                break
            await asyncio.sleep(self._backoff_seconds * (2**attempt))

        raise ProviderError(
            f'TwelveData request exhausted retries: {last_exception}',
            code='provider_retries_exhausted',
            provider='twelvedata',
            retryable=False,
        )
