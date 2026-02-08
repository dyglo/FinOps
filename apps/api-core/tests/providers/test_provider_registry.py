from __future__ import annotations

import os

import pytest

from finops_api.config import get_settings
from finops_api.providers.base import ProviderError
from finops_api.providers.registry import get_search_provider
from finops_api.providers.serpapi.client import SerpApiAdapter
from finops_api.providers.serper.client import SerperAdapter
from finops_api.providers.tavily.client import TavilyAdapter


def test_registry_resolves_tavily_provider() -> None:
    os.environ['TAVILY_API_KEY'] = 'test-key'
    get_settings.cache_clear()
    provider = get_search_provider('tavily')
    assert isinstance(provider, TavilyAdapter)


def test_registry_resolves_serper_provider() -> None:
    os.environ['SERPERDEV_API_KEY'] = 'test-key'
    get_settings.cache_clear()
    provider = get_search_provider('serper')
    assert isinstance(provider, SerperAdapter)


def test_registry_resolves_serpapi_provider() -> None:
    os.environ['SERPAPI_API_KEY'] = 'test-key'
    get_settings.cache_clear()
    provider = get_search_provider('serpapi')
    assert isinstance(provider, SerpApiAdapter)


def test_registry_rejects_unknown_provider() -> None:
    with pytest.raises(ProviderError, match='Unsupported search provider'):
        get_search_provider('unknown')
