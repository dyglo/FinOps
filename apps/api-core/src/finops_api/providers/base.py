from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ProviderError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = 'provider_error',
        provider: str | None = None,
        http_status: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.provider = provider
        self.http_status = http_status
        self.retryable = retryable

    def __str__(self) -> str:
        return self.message


@dataclass(slots=True)
class ProviderResponse:
    http_status: int
    provider_request_id: str | None
    payload: dict[str, object]


class SearchProvider(Protocol):
    async def fetch_news(
        self,
        *,
        idempotency_key: str,
        request_payload: dict[str, object],
    ) -> ProviderResponse:
        ...
