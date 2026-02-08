from __future__ import annotations

import hashlib
import json
from typing import Any, cast


def stable_payload_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def provider_cache_key(*, org_id: str, provider: str, resource: str, payload_hash: str) -> str:
    return f'ingestion:{provider}:{resource}:{org_id}:{payload_hash}'


async def get_cached_payload(redis_client: Any, key: str) -> dict[str, object] | None:
    raw = await redis_client.get(key)
    if raw is None:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8')
    return cast(dict[str, object], json.loads(raw))


async def set_cached_payload(
    redis_client: Any,
    *,
    key: str,
    payload: dict[str, object],
    ttl_seconds: int,
) -> None:
    await redis_client.set(key, json.dumps(payload), ex=ttl_seconds)
