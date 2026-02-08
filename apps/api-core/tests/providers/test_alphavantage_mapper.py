from __future__ import annotations

from finops_api.providers.alphavantage.dto import (
    AlphaVantageQuoteResponse,
    AlphaVantageTimeseriesResponse,
)
from finops_api.providers.alphavantage.mapper import (
    to_canonical_quote,
    to_canonical_timeseries,
)


def test_alphavantage_quote_mapper() -> None:
    payload = AlphaVantageQuoteResponse.model_validate(
        {
            'Global Quote': {
                '01. symbol': 'AAPL',
                '05. price': '189.25',
                '07. latest trading day': '2026-02-09',
                '10. change percent': '1.15%',
            }
        }
    )
    quote = to_canonical_quote(payload)
    assert quote.symbol == 'AAPL'
    assert quote.price == 189.25
    assert quote.change_percent == 1.15


def test_alphavantage_timeseries_mapper() -> None:
    payload = AlphaVantageTimeseriesResponse.model_validate(
        {
            'Meta Data': {'2. Symbol': 'AAPL'},
            'Time Series (Daily)': {
                '2026-02-08': {
                    '1. open': '187.0',
                    '2. high': '190.0',
                    '3. low': '186.0',
                    '4. close': '189.0',
                    '5. volume': '1000',
                }
            },
        }
    )
    rows = to_canonical_timeseries(payload, symbol='AAPL', timeframe='1day')
    assert len(rows) == 1
    assert rows[0].symbol == 'AAPL'
    assert rows[0].close == 189.0
