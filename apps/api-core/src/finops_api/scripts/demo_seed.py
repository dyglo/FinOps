from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import text

from finops_api.db import SessionLocal
from finops_api.models import (
    IngestionJob,
    IngestionRawPayload,
    MarketQuote,
    MarketTimeseries,
    NewsDocument,
    SignalFeature,
)
from finops_api.services.cache import stable_payload_hash


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Seed demo data for local frontend development.')
    parser.add_argument(
        '--org-id',
        type=UUID,
        default=UUID('00000000-0000-0000-0000-000000000001'),
        help='Tenant org UUID used to scope seeded data.',
    )
    parser.add_argument(
        '--symbol',
        type=str,
        default='AAPL',
        help='Ticker symbol to seed for market and signal endpoints.',
    )
    return parser.parse_args()


async def run_seed(*, org_id: UUID, symbol: str) -> None:
    now = datetime.now(UTC)
    symbol = symbol.upper()
    run_tag = now.strftime('%Y%m%d%H%M%S')

    news_request_payload = {'query': f'{symbol} earnings', 'max_results': 5}
    market_request_payload = {'symbol': symbol, 'interval': '1day', 'outputsize': 30}
    quote_request_payload = {'symbol': symbol}

    async with SessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.current_org_id', :org_id, false)"),
            {'org_id': str(org_id)},
        )

        news_job = IngestionJob(
            org_id=org_id,
            provider='tavily',
            resource='news_search',
            status='completed',
            idempotency_key=f'demo-news-{symbol.lower()}-{run_tag}',
            payload=news_request_payload,
            schema_version='v1',
            attempt_count=1,
            started_at=now - timedelta(seconds=15),
            completed_at=now - timedelta(seconds=12),
        )
        market_job = IngestionJob(
            org_id=org_id,
            provider='twelvedata',
            resource='market_timeseries_backfill',
            status='completed',
            idempotency_key=f'demo-market-{symbol.lower()}-{run_tag}',
            payload=market_request_payload,
            schema_version='v1',
            attempt_count=1,
            started_at=now - timedelta(seconds=10),
            completed_at=now - timedelta(seconds=8),
        )
        quote_job = IngestionJob(
            org_id=org_id,
            provider='twelvedata',
            resource='market_quote_refresh',
            status='completed',
            idempotency_key=f'demo-quote-{symbol.lower()}-{run_tag}',
            payload=quote_request_payload,
            schema_version='v1',
            attempt_count=1,
            started_at=now - timedelta(seconds=6),
            completed_at=now - timedelta(seconds=4),
        )
        session.add_all([news_job, market_job, quote_job])
        await session.flush()

        news_response_payload: dict[str, object] = {
            'query': news_request_payload['query'],
            'results': [
                {
                    'title': f'{symbol} outlook strengthened after latest quarter',
                    'url': f'https://example.com/{symbol.lower()}/outlook-{run_tag}',
                    'content': 'Guidance and margins improved.',
                },
                {
                    'title': f'{symbol} supply chain commentary update',
                    'url': f'https://example.com/{symbol.lower()}/supply-{run_tag}',
                    'content': 'Operations and channel inventory normalizing.',
                },
            ],
        }
        news_raw = IngestionRawPayload(
            org_id=org_id,
            job_id=news_job.id,
            provider='tavily',
            resource='news_search',
            schema_version='v1',
            content_hash=stable_payload_hash(news_response_payload),
            request_payload=news_request_payload,
            response_payload=news_response_payload,
            http_status=200,
            provider_request_id=f'demo-news-{run_tag}',
            fetched_at=now - timedelta(seconds=11),
        )

        market_response_payload: dict[str, object] = {
            'symbol': symbol,
            'interval': '1day',
            'values': [{'datetime': (now - timedelta(days=i)).isoformat()} for i in range(5)],
        }
        market_raw = IngestionRawPayload(
            org_id=org_id,
            job_id=market_job.id,
            provider='twelvedata',
            resource='market_timeseries_backfill',
            schema_version='v1',
            content_hash=stable_payload_hash(market_response_payload),
            request_payload=market_request_payload,
            response_payload=market_response_payload,
            http_status=200,
            provider_request_id=f'demo-market-{run_tag}',
            fetched_at=now - timedelta(seconds=7),
        )

        quote_response_payload: dict[str, object] = {
            'symbol': symbol,
            'close': 215.42,
            'percent_change': 0.73,
            'timestamp': now.isoformat(),
        }
        quote_raw = IngestionRawPayload(
            org_id=org_id,
            job_id=quote_job.id,
            provider='twelvedata',
            resource='market_quote_refresh',
            schema_version='v1',
            content_hash=stable_payload_hash(quote_response_payload),
            request_payload=quote_request_payload,
            response_payload=quote_response_payload,
            http_status=200,
            provider_request_id=f'demo-quote-{run_tag}',
            fetched_at=now - timedelta(seconds=3),
        )
        session.add_all([news_raw, market_raw, quote_raw])
        await session.flush()

        news_docs = [
            NewsDocument(
                org_id=org_id,
                job_id=news_job.id,
                raw_payload_id=news_raw.id,
                source_provider='tavily',
                normalization_version='v1',
                source_url=f'https://example.com/{symbol.lower()}/outlook-{run_tag}',
                title=f'{symbol} outlook strengthened after latest quarter',
                snippet='Guidance and margins improved.',
                author='Demo Seed',
                language='en',
                published_at=now - timedelta(hours=4),
                document_hash=stable_payload_hash(
                    {'symbol': symbol, 'topic': 'outlook', 'run': run_tag}
                ),
                created_at=now - timedelta(seconds=11),
            ),
            NewsDocument(
                org_id=org_id,
                job_id=news_job.id,
                raw_payload_id=news_raw.id,
                source_provider='tavily',
                normalization_version='v1',
                source_url=f'https://example.com/{symbol.lower()}/supply-{run_tag}',
                title=f'{symbol} supply chain commentary update',
                snippet='Operations and channel inventory normalizing.',
                author='Demo Seed',
                language='en',
                published_at=now - timedelta(hours=2),
                document_hash=stable_payload_hash(
                    {'symbol': symbol, 'topic': 'supply', 'run': run_tag}
                ),
                created_at=now - timedelta(seconds=10),
            ),
        ]
        session.add_all(news_docs)

        ts_rows = []
        for idx in range(5):
            ts = (now - timedelta(days=idx)).replace(hour=16, minute=0, second=0, microsecond=0)
            base = 210.0 - idx
            ts_rows.append(
                MarketTimeseries(
                    org_id=org_id,
                    symbol=symbol,
                    timeframe='1day',
                    provider='twelvedata',
                    schema_version='v1',
                    raw_payload_id=market_raw.id,
                    ts=ts,
                    open=base,
                    high=base + 2.0,
                    low=base - 1.5,
                    close=base + 0.9,
                    volume=1250000 + (idx * 18000),
                    fetched_at=now - timedelta(seconds=7),
                )
            )
        session.add_all(ts_rows)

        quote_row = MarketQuote(
            org_id=org_id,
            symbol=symbol,
            provider='twelvedata',
            schema_version='v1',
            raw_payload_id=quote_raw.id,
            price=215.42,
            change_percent=0.73,
            as_of=now - timedelta(minutes=1),
            fetched_at=now - timedelta(seconds=3),
        )
        session.add(quote_row)

        signal_rows = [
            SignalFeature(
                org_id=org_id,
                symbol=symbol,
                feature_name='news_sentiment_mean',
                feature_version='v1',
                value=0.62,
                meta={'source': 'demo_seed', 'window': '24h'},
            ),
            SignalFeature(
                org_id=org_id,
                symbol=symbol,
                feature_name='news_momentum',
                feature_version='v1',
                value=0.41,
                meta={'source': 'demo_seed', 'window': '24h'},
            ),
        ]
        session.add_all(signal_rows)
        await session.commit()

    print(f'Seeded demo data for org_id={org_id} symbol={symbol} run={run_tag}')


def main() -> None:
    import asyncio

    args = parse_args()
    asyncio.run(run_seed(org_id=args.org_id, symbol=args.symbol))


if __name__ == '__main__':
    main()
