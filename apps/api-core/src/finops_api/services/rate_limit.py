from __future__ import annotations

import json
import time
from typing import Any


def provider_rate_limit_key(*, provider: str, org_id: str) -> str:
    return f'ratelimit:{provider}:{org_id}'


async def take_provider_token(
    redis_client: Any,
    *,
    provider: str,
    org_id: str,
    limit_per_minute: int,
    now_seconds: float | None = None,
) -> bool:
    key = provider_rate_limit_key(provider=provider, org_id=org_id)
    if limit_per_minute <= 0:
        return False

    current_time = now_seconds if now_seconds is not None else time.time()
    capacity = float(max(1, limit_per_minute))
    refill_rate = float(limit_per_minute) / 60.0

    raw_state = await redis_client.get(key)
    if raw_state is None:
        tokens = capacity
        last_refill = current_time
    else:
        if isinstance(raw_state, bytes):
            raw_state = raw_state.decode('utf-8')
        state = json.loads(raw_state)
        tokens = float(state.get('tokens', capacity))
        last_refill = float(state.get('last_refill', current_time))

    elapsed = max(0.0, current_time - last_refill)
    tokens = min(capacity, tokens + (elapsed * refill_rate))

    allowed = tokens >= 1.0
    if allowed:
        tokens -= 1.0

    state_payload = json.dumps(
        {
            'tokens': tokens,
            'last_refill': current_time,
            'capacity': capacity,
            'refill_per_second': refill_rate,
        }
    )
    await redis_client.set(key, state_payload, ex=120)
    return allowed
