from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text

from finops_api.config import get_settings
from finops_api.db import SessionLocal
from finops_api.models import NewsDocument
from finops_api.providers.alphavantage.dto import (
    AlphaVantageQuoteResponse,
    AlphaVantageTimeseriesResponse,
)
from finops_api.providers.alphavantage.mapper import (
    to_canonical_quote as alphavantage_to_canonical_quote,
)
from finops_api.providers.alphavantage.mapper import (
    to_canonical_timeseries as alphavantage_to_canonical_timeseries,
)
from finops_api.providers.base import ProviderError, ProviderResponse
from finops_api.providers.registry import get_market_data_provider, get_search_provider
from finops_api.providers.serpapi.dto import SerpApiSearchResponse
from finops_api.providers.serpapi.mapper import (
    to_canonical_news_item as serpapi_to_canonical_news_item,
)
from finops_api.providers.serper.dto import SerperNewsResponse
from finops_api.providers.serper.mapper import (
    to_canonical_news_item as serper_to_canonical_news_item,
)
from finops_api.providers.tavily.dto import TavilySearchResponse
from finops_api.providers.tavily.mapper import (
    to_canonical_news_item as tavily_to_canonical_news_item,
)
from finops_api.providers.twelvedata.dto import (
    TwelveDataQuoteResponse,
    TwelveDataTimeseriesResponse,
)
from finops_api.providers.twelvedata.mapper import to_canonical_quote, to_canonical_timeseries
from finops_api.repositories.ingestion import IngestionRepository
from finops_api.repositories.ingestion_raw_payloads import IngestionRawPayloadRepository
from finops_api.repositories.market import MarketRepository
from finops_api.repositories.news_documents import NewsDocumentRepository
from finops_api.services.cache import (
    get_cached_payload,
    provider_cache_key,
    set_cached_payload,
    stable_payload_hash,
)
from finops_api.services.rate_limit import take_provider_token


def _provider_rate_limit_per_minute(provider: str) -> int:
    settings = get_settings()
    if provider == 'tavily':
        return settings.tavily_rate_limit_per_minute
    if provider == 'serper':
        return settings.serper_rate_limit_per_minute
    if provider == 'serpapi':
        return settings.serpapi_rate_limit_per_minute
    if provider == 'twelvedata':
        return settings.twelvedata_rate_limit_per_minute
    if provider == 'alphavantage':
        return settings.alphavantage_rate_limit_per_minute
    return 0


def _build_documents(
    *,
    org_id: UUID,
    job_id: UUID,
    raw_payload_id: UUID,
    provider: str,
    cached_payload: dict[str, object],
) -> list[NewsDocument]:
    documents: list[NewsDocument] = []

    if provider == 'tavily':
        tavily_response = TavilySearchResponse.model_validate(cached_payload)
        for tavily_item in tavily_response.results:
            normalized_tavily = tavily_to_canonical_news_item(tavily_item)
            documents.append(
                NewsDocument(
                    org_id=org_id,
                    job_id=job_id,
                    raw_payload_id=raw_payload_id,
                    source_provider=normalized_tavily.source_provider,
                    normalization_version='v1',
                    source_url=normalized_tavily.source_url,
                    title=normalized_tavily.title,
                    snippet=normalized_tavily.snippet,
                    author=normalized_tavily.author,
                    language=normalized_tavily.language,
                    published_at=normalized_tavily.published_at,
                    document_hash=normalized_tavily.document_hash,
                    created_at=datetime.now(UTC),
                )
            )
        return documents

    if provider == 'serper':
        serper_response = SerperNewsResponse.model_validate(cached_payload)
        for serper_item in serper_response.news:
            normalized_serper = serper_to_canonical_news_item(serper_item)
            documents.append(
                NewsDocument(
                    org_id=org_id,
                    job_id=job_id,
                    raw_payload_id=raw_payload_id,
                    source_provider=normalized_serper.source_provider,
                    normalization_version='v1',
                    source_url=normalized_serper.source_url,
                    title=normalized_serper.title,
                    snippet=normalized_serper.snippet,
                    author=normalized_serper.author,
                    language=normalized_serper.language,
                    published_at=normalized_serper.published_at,
                    document_hash=normalized_serper.document_hash,
                    created_at=datetime.now(UTC),
                )
            )
        return documents

    if provider == 'serpapi':
        serpapi_response = SerpApiSearchResponse.model_validate(cached_payload)
        for serpapi_item in serpapi_response.news_results:
            normalized_serpapi = serpapi_to_canonical_news_item(serpapi_item)
            documents.append(
                NewsDocument(
                    org_id=org_id,
                    job_id=job_id,
                    raw_payload_id=raw_payload_id,
                    source_provider=normalized_serpapi.source_provider,
                    normalization_version='v1',
                    source_url=normalized_serpapi.source_url,
                    title=normalized_serpapi.title,
                    snippet=normalized_serpapi.snippet,
                    author=normalized_serpapi.author,
                    language=normalized_serpapi.language,
                    published_at=normalized_serpapi.published_at,
                    document_hash=normalized_serpapi.document_hash,
                    created_at=datetime.now(UTC),
                )
            )
        return documents

    raise ProviderError(
        f'Unsupported provider for normalization: {provider}',
        code='provider_unsupported',
        provider=provider,
        retryable=False,
    )


async def process_ingestion_job(
    *,
    job_id: UUID,
    org_id: UUID,
    redis_client: Any,
) -> dict[str, object]:
    settings = get_settings()

    async with SessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.current_org_id', :org_id, false)"),
            {'org_id': str(org_id)},
        )

        ingestion_repo = IngestionRepository(session)
        raw_repo = IngestionRawPayloadRepository(session)
        news_repo = NewsDocumentRepository(session)
        market_repo = MarketRepository(session)

        job = await ingestion_repo.get(org_id=org_id, job_id=job_id)
        if job is None:
            raise ProviderError(f'Ingestion job not found: {job_id}')

        if job.status == 'completed':
            return {
                'status': 'completed',
                'job_id': str(job.id),
                'normalized_count': 0,
                'cache_hit': False,
            }

        await ingestion_repo.mark_running(job)
        try:
            payload_hash = stable_payload_hash(job.payload)
            cache_key = provider_cache_key(
                org_id=str(org_id),
                provider=job.provider,
                resource=job.resource,
                payload_hash=payload_hash,
            )

            cached_payload = await get_cached_payload(redis_client, cache_key)
            cache_hit = cached_payload is not None

            if cached_payload is None:
                provider_response: ProviderResponse
                allowed = await take_provider_token(
                    redis_client,
                    provider=job.provider,
                    org_id=str(org_id),
                    limit_per_minute=_provider_rate_limit_per_minute(job.provider),
                )
                if not allowed:
                    raise ProviderError(f'Provider rate limit exceeded for {job.provider}')

                if job.resource == 'news_search':
                    search_adapter = get_search_provider(job.provider)
                    provider_response = await search_adapter.search_news(
                        idempotency_key=job.idempotency_key,
                        request_payload=job.payload,
                    )
                elif job.resource == 'market_timeseries_backfill':
                    market_adapter = get_market_data_provider(job.provider)
                    provider_response = await market_adapter.get_timeseries(
                        idempotency_key=job.idempotency_key,
                        request_payload=job.payload,
                    )
                elif job.resource == 'market_quote_refresh':
                    market_adapter = get_market_data_provider(job.provider)
                    provider_response = await market_adapter.get_quote(
                        idempotency_key=job.idempotency_key,
                        request_payload=job.payload,
                    )
                else:
                    raise ProviderError(
                        f'Unsupported ingestion resource: {job.resource}',
                        code='resource_unsupported',
                        provider=job.provider,
                        retryable=False,
                    )
                cached_payload = provider_response.payload
                await set_cached_payload(
                    redis_client,
                    key=cache_key,
                    payload=cached_payload,
                    ttl_seconds=settings.provider_cache_ttl_seconds,
                )

            raw_payload_hash = stable_payload_hash(cached_payload)
            raw_payload = await raw_repo.create(
                org_id=org_id,
                job_id=job.id,
                provider=job.provider,
                resource=job.resource,
                content_hash=raw_payload_hash,
                request_payload=job.payload,
                response_payload=cached_payload,
                http_status=200,
                provider_request_id=None,
            )

            normalized_count = 0
            if job.resource == 'news_search':
                documents = _build_documents(
                    org_id=org_id,
                    job_id=job.id,
                    raw_payload_id=raw_payload.id,
                    provider=job.provider,
                    cached_payload=cached_payload,
                )
                if documents:
                    await news_repo.create_many(documents)
                normalized_count = len(documents)
            elif job.resource == 'market_timeseries_backfill':
                if job.provider == 'twelvedata':
                    twelvedata_timeseries = TwelveDataTimeseriesResponse.model_validate(
                        cached_payload
                    )
                    rows = [
                        row.model_dump()
                        for row in to_canonical_timeseries(twelvedata_timeseries)
                    ]
                elif job.provider == 'alphavantage':
                    av_timeseries_response = AlphaVantageTimeseriesResponse.model_validate(
                        cached_payload
                    )
                    symbol = str(job.payload.get('symbol', '')).upper()
                    interval = str(job.payload.get('interval', '1day'))
                    rows = [
                        row.model_dump()
                        for row in alphavantage_to_canonical_timeseries(
                            av_timeseries_response,
                            symbol=symbol,
                            timeframe=interval,
                        )
                    ]
                else:
                    raise ProviderError(
                        f'Unsupported market provider for timeseries: {job.provider}',
                        code='provider_unsupported',
                        provider=job.provider,
                        retryable=False,
                    )
                normalized_count = await market_repo.upsert_timeseries_rows(
                    org_id=org_id,
                    provider=job.provider,
                    schema_version='v1',
                    raw_payload_id=raw_payload.id,
                    rows=rows,
                )
            elif job.resource == 'market_quote_refresh':
                if job.provider == 'twelvedata':
                    twelvedata_quote = TwelveDataQuoteResponse.model_validate(cached_payload)
                    mapped_quote = to_canonical_quote(twelvedata_quote)
                    canonical_symbol = mapped_quote.symbol
                    canonical_price = mapped_quote.price
                    canonical_change_percent = mapped_quote.change_percent
                    canonical_as_of = mapped_quote.as_of
                elif job.provider == 'alphavantage':
                    av_quote_response = AlphaVantageQuoteResponse.model_validate(cached_payload)
                    av_quote = alphavantage_to_canonical_quote(av_quote_response)
                    canonical_symbol = av_quote.symbol
                    canonical_price = av_quote.price
                    canonical_change_percent = av_quote.change_percent
                    canonical_as_of = av_quote.as_of
                else:
                    raise ProviderError(
                        f'Unsupported market provider for quote: {job.provider}',
                        code='provider_unsupported',
                        provider=job.provider,
                        retryable=False,
                    )
                await market_repo.upsert_quote(
                    org_id=org_id,
                    provider=job.provider,
                    schema_version='v1',
                    raw_payload_id=raw_payload.id,
                    symbol=canonical_symbol,
                    price=canonical_price,
                    change_percent=canonical_change_percent,
                    as_of=canonical_as_of,
                )
                normalized_count = 1

            await ingestion_repo.mark_completed(job)

            return {
                'status': 'completed',
                'job_id': str(job.id),
                'normalized_count': normalized_count,
                'cache_hit': cache_hit,
            }
        except Exception as exc:
            await ingestion_repo.mark_failed(job, str(exc))
            raise
