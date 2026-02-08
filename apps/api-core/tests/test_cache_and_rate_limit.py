from __future__ import annotations

import pytest

from finops_api.services.cache import (
    get_cached_payload,
    provider_cache_key,
    set_cached_payload,
    stable_payload_hash,
)
from finops_api.services.rate_limit import provider_rate_limit_key, take_provider_token


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int) -> None:  # noqa: ARG002
        self.store[key] = value


def test_stable_payload_hash_is_deterministic() -> None:
    payload = {'query': 'nvda', 'max_results': 5}
    assert stable_payload_hash(payload) == stable_payload_hash(payload)


def test_cache_key_and_rate_limit_key_are_stable() -> None:
    assert provider_cache_key(
        org_id='org1', provider='tavily', resource='news_search', payload_hash='abc'
    ) == 'ingestion:tavily:news_search:org1:abc'
    assert provider_rate_limit_key(provider='tavily', org_id='org1') == 'ratelimit:tavily:org1'


@pytest.mark.asyncio
async def test_cache_round_trip() -> None:
    redis = FakeRedis()
    key = 'k'
    payload = {'query': 'test'}

    await set_cached_payload(redis, key=key, payload=payload, ttl_seconds=300)
    cached = await get_cached_payload(redis, key)
    assert cached == payload


@pytest.mark.asyncio
async def test_rate_limit_bucket() -> None:
    redis = FakeRedis()

    assert await take_provider_token(
        redis,
        provider='tavily',
        org_id='org1',
        limit_per_minute=2,
    )
    assert await take_provider_token(
        redis,
        provider='tavily',
        org_id='org1',
        limit_per_minute=2,
    )
    assert not await take_provider_token(
        redis,
        provider='tavily',
        org_id='org1',
        limit_per_minute=2,
    )


@pytest.mark.asyncio
async def test_rate_limit_bucket_refills_over_time() -> None:
    redis = FakeRedis()

    assert await take_provider_token(
        redis,
        provider='tavily',
        org_id='org1',
        limit_per_minute=2,
        now_seconds=100.0,
    )
    assert await take_provider_token(
        redis,
        provider='tavily',
        org_id='org1',
        limit_per_minute=2,
        now_seconds=100.0,
    )
    assert not await take_provider_token(
        redis,
        provider='tavily',
        org_id='org1',
        limit_per_minute=2,
        now_seconds=100.0,
    )

    assert await take_provider_token(
        redis,
        provider='tavily',
        org_id='org1',
        limit_per_minute=2,
        now_seconds=130.0,
    )


@pytest.mark.asyncio
async def test_rate_limit_bucket_is_isolated_per_org() -> None:
    redis = FakeRedis()

    assert await take_provider_token(
        redis,
        provider='tavily',
        org_id='org-a',
        limit_per_minute=1,
        now_seconds=200.0,
    )
    assert not await take_provider_token(
        redis,
        provider='tavily',
        org_id='org-a',
        limit_per_minute=1,
        now_seconds=200.0,
    )
    assert await take_provider_token(
        redis,
        provider='tavily',
        org_id='org-b',
        limit_per_minute=1,
        now_seconds=200.0,
    )
