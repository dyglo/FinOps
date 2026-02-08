from __future__ import annotations

import asyncio
from typing import Any, cast

import httpx

from finops_api.config import get_settings
from finops_api.providers.base import ProviderError, ProviderResponse
from finops_api.providers.tavily.dto import TavilySearchRequest, TavilySearchResponse


class TavilyAdapter:
    def __init__(
        self,
        *,
        base_url: str = 'https://api.tavily.com',
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        backoff_seconds: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        if not settings.tavily_api_key:
            raise ProviderError(
                'TAVILY_API_KEY is not configured',
                code='provider_config_error',
                provider='tavily',
                retryable=False,
            )

        self._api_key = settings.tavily_api_key
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
                provider='tavily',
                retryable=False,
            )
        self._transport = transport

    async def fetch_news(
        self,
        *,
        idempotency_key: str,
        request_payload: dict[str, object],
    ) -> ProviderResponse:
        request = TavilySearchRequest.model_validate(request_payload)
        response = await self._post_with_retry(idempotency_key=idempotency_key, request=request)
        parsed = TavilySearchResponse.model_validate(response)

        return ProviderResponse(
            http_status=200,
            provider_request_id=None,
            payload=parsed.model_dump(mode='json'),
        )

    async def _post_with_retry(
        self,
        *,
        idempotency_key: str,
        request: TavilySearchRequest,
    ) -> dict[str, Any]:
        body = request.model_dump(mode='json')
        body['api_key'] = self._api_key

        headers = {
            'Content-Type': 'application/json',
            'Idempotency-Key': idempotency_key,
        }

        last_exception: Exception | None = None
        timeout = httpx.Timeout(self._timeout_seconds)
        url = f'{self._base_url}/search'

        for attempt in range(self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout, transport=self._transport) as client:
                    response = await client.post(url, json=body, headers=headers)

                if response.status_code in {429, 500, 502, 503, 504}:
                    raise ProviderError(
                        f'Tavily transient error: {response.status_code}',
                        code='provider_transient_error',
                        provider='tavily',
                        http_status=response.status_code,
                        retryable=True,
                    )
                if response.status_code >= 400:
                    raise ProviderError(
                        f'Tavily request failed: {response.status_code} {response.text}',
                        code='provider_request_failed',
                        provider='tavily',
                        http_status=response.status_code,
                        retryable=False,
                    )

                return cast(dict[str, Any], response.json())
            except httpx.TimeoutException as exc:
                last_exception = ProviderError(
                    f'Tavily timeout: {exc}',
                    code='provider_timeout',
                    provider='tavily',
                    retryable=True,
                )
            except httpx.NetworkError as exc:
                last_exception = ProviderError(
                    f'Tavily network error: {exc}',
                    code='provider_network_error',
                    provider='tavily',
                    retryable=True,
                )
            except ProviderError as exc:
                last_exception = exc

            assert last_exception is not None
            if attempt == self._max_retries or not last_exception.retryable:
                break

            await asyncio.sleep(self._backoff_seconds * (2**attempt))
        raise ProviderError(
            f'Tavily request exhausted retries: {last_exception}',
            code='provider_retries_exhausted',
            provider='tavily',
            retryable=False,
        )
