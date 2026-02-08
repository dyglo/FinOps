from __future__ import annotations

from finops_api.providers.twelvedata.dto import (
    CanonicalQuote,
    CanonicalTimeseriesPoint,
    TwelveDataQuoteResponse,
    TwelveDataTimeseriesResponse,
    parse_datetime,
)


def to_canonical_quote(payload: TwelveDataQuoteResponse) -> CanonicalQuote:
    change_percent = (
        float(payload.percent_change) if payload.percent_change is not None else None
    )
    return CanonicalQuote(
        symbol=payload.symbol.upper(),
        price=float(payload.close),
        change_percent=change_percent,
        as_of=payload.as_of(),
    )


def to_canonical_timeseries(
    payload: TwelveDataTimeseriesResponse,
) -> list[CanonicalTimeseriesPoint]:
    symbol = payload.meta.symbol.upper()
    timeframe = payload.meta.interval
    rows: list[CanonicalTimeseriesPoint] = []
    for value in payload.values:
        rows.append(
            CanonicalTimeseriesPoint(
                symbol=symbol,
                timeframe=timeframe,
                ts=parse_datetime(value.datetime),
                open=float(value.open),
                high=float(value.high),
                low=float(value.low),
                close=float(value.close),
                volume=float(value.volume),
            )
        )
    return rows
