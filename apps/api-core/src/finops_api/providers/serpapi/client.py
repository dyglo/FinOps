from __future__ import annotations

import asyncio
from typing import cast

import httpx

from finops_api.config import get_settings
from finops_api.providers.base import ProviderError, ProviderResponse
from finops_api.providers.serpapi.dto import SerpApiSearchRequest


class SerpApiAdapter:
    def __init__(
        self,
        *,
        base_url: str = 'https://serpapi.com',
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        backoff_seconds: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        if not settings.serpapi_api_key:
            raise ProviderError(
                'SERPAPI_API_KEY is not configured',
                code='provider_config_error',
                provider='serpapi',
                retryable=False,
            )
        self._api_key = settings.serpapi_api_key
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
                provider='serpapi',
                retryable=False,
            )
        self._transport = transport

    async def search_news(
        self,
        *,
        idempotency_key: str,
        request_payload: dict[str, object],
    ) -> ProviderResponse:
        request = SerpApiSearchRequest.model_validate(request_payload)
        params = request.model_dump(mode='json')
        params['api_key'] = self._api_key
        payload = await self._get_with_retry(
            path='/search.json',
            idempotency_key=idempotency_key,
            params=params,
        )
        return ProviderResponse(
            http_status=200,
            provider_request_id=None,
            payload=payload,
        )

    async def search_web(
        self,
        *,
        idempotency_key: str,
        request_payload: dict[str, object],
    ) -> ProviderResponse:
        request = SerpApiSearchRequest.model_validate(request_payload)
        params = request.model_dump(mode='json')
        params['engine'] = 'google'
        params['api_key'] = self._api_key
        payload = await self._get_with_retry(
            path='/search.json',
            idempotency_key=idempotency_key,
            params=params,
        )
        return ProviderResponse(
            http_status=200,
            provider_request_id=None,
            payload=payload,
        )

    async def _get_with_retry(
        self,
        *,
        path: str,
        idempotency_key: str,
        params: dict[str, object],
    ) -> dict[str, object]:
        headers = {'Idempotency-Key': idempotency_key}
        query_params = {key: str(value) for key, value in params.items()}
        timeout = httpx.Timeout(self._timeout_seconds)
        url = f'{self._base_url}{path}'
        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout, transport=self._transport) as client:
                    response = await client.get(url, params=query_params, headers=headers)

                if response.status_code in {429, 500, 502, 503, 504}:
                    raise ProviderError(
                        f'SerpAPI transient error: {response.status_code}',
                        code='provider_transient_error',
                        provider='serpapi',
                        http_status=response.status_code,
                        retryable=True,
                    )
                if response.status_code >= 400:
                    raise ProviderError(
                        f'SerpAPI request failed: {response.status_code} {response.text}',
                        code='provider_request_failed',
                        provider='serpapi',
                        http_status=response.status_code,
                        retryable=False,
                    )
                return cast(dict[str, object], response.json())
            except httpx.TimeoutException as exc:
                last_exception = ProviderError(
                    f'SerpAPI timeout: {exc}',
                    code='provider_timeout',
                    provider='serpapi',
                    retryable=True,
                )
            except httpx.NetworkError as exc:
                last_exception = ProviderError(
                    f'SerpAPI network error: {exc}',
                    code='provider_network_error',
                    provider='serpapi',
                    retryable=True,
                )
            except ProviderError as exc:
                last_exception = exc

            assert last_exception is not None
            if attempt == self._max_retries or not last_exception.retryable:
                break
            await asyncio.sleep(self._backoff_seconds * (2**attempt))

        raise ProviderError(
            f'SerpAPI request exhausted retries: {last_exception}',
            code='provider_retries_exhausted',
            provider='serpapi',
            retryable=False,
        )
