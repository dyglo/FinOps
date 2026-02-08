from __future__ import annotations

from finops_api.providers.twelvedata.dto import (
    TwelveDataQuoteResponse,
    TwelveDataTimeseriesResponse,
)
from finops_api.providers.twelvedata.mapper import to_canonical_quote, to_canonical_timeseries


def test_twelvedata_quote_mapper() -> None:
    payload = TwelveDataQuoteResponse(
        symbol='aapl',
        close='189.25',
        percent_change='1.15',
        datetime='2026-02-09T10:00:00Z',
    )
    mapped = to_canonical_quote(payload)
    assert mapped.symbol == 'AAPL'
    assert mapped.price == 189.25
    assert mapped.change_percent == 1.15


def test_twelvedata_timeseries_mapper() -> None:
    payload = TwelveDataTimeseriesResponse.model_validate(
        {
            'meta': {'symbol': 'AAPL', 'interval': '1day'},
            'values': [
                {
                    'datetime': '2026-02-08',
                    'open': '187.0',
                    'high': '190.0',
                    'low': '186.0',
                    'close': '189.0',
                    'volume': '1000',
                }
            ],
        }
    )
    rows = to_canonical_timeseries(payload)
    assert len(rows) == 1
    assert rows[0].symbol == 'AAPL'
    assert rows[0].timeframe == '1day'
    assert rows[0].close == 189.0
