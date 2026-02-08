'use client';

import { memo, useEffect, useRef, useState } from 'react';

type TradingViewAdvancedChartProps = {
  symbol?: string;
};

function TradingViewAdvancedChart({ symbol = 'NASDAQ:AAPL' }: TradingViewAdvancedChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    container.innerHTML =
      '<div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>' +
      '<div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div>';

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      allow_symbol_change: true,
      calendar: false,
      details: false,
      hide_side_toolbar: false,
      hide_top_toolbar: false,
      hide_legend: false,
      hide_volume: false,
      hotlist: false,
      interval: 'D',
      locale: 'en',
      save_image: true,
      style: '1',
      symbol,
      theme: 'dark',
      timezone: 'Etc/UTC',
      backgroundColor: '#0F0F0F',
      gridColor: 'rgba(242, 242, 242, 0.06)',
      watchlist: [],
      withdateranges: false,
      compareSymbols: [],
      show_popup_button: true,
      popup_height: '650',
      popup_width: '1000',
      studies: [],
      autosize: true,
    });

    script.onerror = () => {
      setFailed(true);
    };

    container.appendChild(script);

    return () => {
      container.innerHTML = '';
    };
  }, [symbol]);

  if (failed) {
    return (
      <div className="flex h-[420px] items-center justify-center rounded-lg border border-[var(--line-soft)] bg-[var(--surface-0)] text-sm text-[var(--text-muted)]">
        TradingView widget failed to load. Verify network/CSP and reload the page.
      </div>
    );
  }

  return <div className="tradingview-widget-container h-[420px] w-full" ref={containerRef} />;
}

export default memo(TradingViewAdvancedChart);
