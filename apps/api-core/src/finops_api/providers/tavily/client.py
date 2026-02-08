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
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        backoff_seconds: float = 0.5,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        if not settings.tavily_api_key:
            raise ProviderError('TAVILY_API_KEY is not configured')

        self._api_key = settings.tavily_api_key
        self._base_url = base_url.rstrip('/')
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._backoff_seconds = backoff_seconds
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
                    raise ProviderError(f'Tavily transient error: {response.status_code}')
                if response.status_code >= 400:
                    raise ProviderError(
                        f'Tavily request failed: {response.status_code} {response.text}'
                    )

                return cast(dict[str, Any], response.json())
            except (httpx.TimeoutException, httpx.NetworkError, ProviderError) as exc:
                last_exception = exc
                if attempt == self._max_retries:
                    break
                if isinstance(exc, ProviderError) and 'failed:' in str(exc):
                    break

                await asyncio.sleep(self._backoff_seconds * (2**attempt))

        raise ProviderError(f'Tavily request exhausted retries: {last_exception}')
