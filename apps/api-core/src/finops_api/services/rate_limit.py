from __future__ import annotations

from typing import Any


def provider_rate_limit_key(*, provider: str, org_id: str) -> str:
    return f'ratelimit:{provider}:{org_id}'


async def take_provider_token(
    redis_client: Any,
    *,
    provider: str,
    org_id: str,
    limit_per_minute: int,
) -> bool:
    key = provider_rate_limit_key(provider=provider, org_id=org_id)
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, 60)
    return int(current) <= limit_per_minute