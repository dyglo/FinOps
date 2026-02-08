from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ProviderError(Exception):
    pass


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
