from __future__ import annotations

from finops_api.providers.base import MarketDataProvider, ProviderError, SearchProvider
from finops_api.providers.serpapi.client import SerpApiAdapter
from finops_api.providers.serper.client import SerperAdapter
from finops_api.providers.tavily.client import TavilyAdapter
from finops_api.providers.twelvedata.client import TwelveDataAdapter


def get_search_provider(provider: str) -> SearchProvider:
    if provider == 'tavily':
        return TavilyAdapter()
    if provider == 'serper':
        return SerperAdapter()
    if provider == 'serpapi':
        return SerpApiAdapter()
    raise ProviderError(
        f'Unsupported search provider: {provider}',
        code='provider_unsupported',
        provider=provider,
        retryable=False,
    )


def get_market_data_provider(provider: str) -> MarketDataProvider:
    if provider == 'twelvedata':
        return TwelveDataAdapter()
    raise ProviderError(
        f'Unsupported market data provider: {provider}',
        code='provider_unsupported',
        provider=provider,
        retryable=False,
    )
