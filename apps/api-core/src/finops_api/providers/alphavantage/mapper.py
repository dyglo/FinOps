from __future__ import annotations

from finops_api.providers.alphavantage.dto import (
    AlphaVantageQuoteResponse,
    AlphaVantageTimeseriesResponse,
    CanonicalQuote,
    CanonicalTimeseriesPoint,
    parse_change_percent,
    parse_date,
)


def to_canonical_quote(payload: AlphaVantageQuoteResponse) -> CanonicalQuote:
    quote = payload.global_quote
    return CanonicalQuote(
        symbol=quote.symbol.upper(),
        price=float(quote.price),
        change_percent=parse_change_percent(quote.change_percent),
        as_of=parse_date(quote.latest_trading_day),
    )


def to_canonical_timeseries(
    payload: AlphaVantageTimeseriesResponse,
    *,
    symbol: str,
    timeframe: str,
) -> list[CanonicalTimeseriesPoint]:
    rows: list[CanonicalTimeseriesPoint] = []
    for ts_key, item in payload.daily.items():
        rows.append(
            CanonicalTimeseriesPoint(
                symbol=symbol.upper(),
                timeframe=timeframe,
                ts=parse_date(ts_key),
                open=float(item.open),
                high=float(item.high),
                low=float(item.low),
                close=float(item.close),
                volume=float(item.volume),
            )
        )
    return rows
