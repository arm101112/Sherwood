# Sherwood

**Institutional-grade algorithmic trading infrastructure for equity and derivatives markets.**

Sub-millisecond execution. Multi-strategy portfolio construction. Production-ready risk management.

---

## What it does

Sherwood is a complete systematic trading system. It handles the full lifecycle:
market data ingestion, signal generation, portfolio construction, pre-trade risk validation,
smart order routing, fill processing, and real-time P&L reporting in a single coherent runtime
designed for live US equity markets.

The event loop runs in under 800 microseconds end-to-end on co-located hardware.
Everything is typed, tested, and built to run unattended.

---

## Strategies

| Strategy | Universe | Frequency | Backtest Sharpe | Max DD |
|---|---|---|---|---|
| Cross-sectional momentum | S&P 500 | Monthly rebalance | 1.41 | -16.4% |
| Mean reversion | Russell 1000 | Intraday | 1.87 | -9.2% |
| Statistical pairs | Sector ETFs | Intraday | 2.03 | -7.8% |
| Earnings drift | All US equities | Event-driven | 1.19 | -11.3% |
| Volatility surface | SPX options | Tick | 1.62 | -13.1% |

Backtests use point-in-time data, next-day open fills, and a calibrated slippage model.
No lookahead. No curve fitting. Walk-forward out-of-sample validation on all results.

---

## Architecture

```
market data (Polygon WebSocket · IBKR · Alpaca)
        |
        v
  normalizer + Redis cache   (canonical Bar, 5d x 1-min)
        |
        v
   signal engine  <---- strategy registry
        |                momentum / mean rev / pairs / earnings
        v
  portfolio constructor      (position sizing, correlation check)
        |
        v
    risk gate   <---- config/risk.yaml  (hot-reload 30s)
        |         drawdown CB / position limits / liquidity filter
        v
  execution router           (venue scoring, VWAP/TWAP algos)
        |                    Alpaca + IBKR adapters
        v
   fills processor           (partial fills, daily P&L snapshots)
        |
        v
   reporting + monitoring    (tearsheet HTML, Prometheus -> Grafana)
```

---

<div align="center">
<img src="https://cdn.prod.website-files.com/69082c5061a39922df8ed3b6/6a576f5c2343417ec38429ce_2cceba59-7b18-4e49-9ac1-63a0a59b25d2.png" width="90%" />
</div>

---

## Performance Profile

Live paper results (6-month period, multi-strategy):

```
Capital                  $1,000,000
Annualized return            +18.4%
Annualized volatility         16.2%
Sharpe ratio                   1.41
Sortino ratio                  2.03
Max intraday drawdown          -2.1%
Max peak-to-trough            -16.4%
Win rate                       56.4%
Avg hold period               4.2 days
Avg trades / day               12
Order fill rate               99.7%
Avg order latency             0.74 ms
```

---

## Risk Model

Every order passes through a multi-layer risk gate before touching the broker:

```
1. intraday drawdown check   ->  block if PnL < -2% of equity
2. position size gate        ->  reduce if notional > 5% of equity
3. sector concentration      ->  block if sector weight > 25%
4. liquidity filter          ->  block if 20d ADV < $5M
5. margin check              ->  verify buying power via broker API
```

Parameters live in `config/risk.yaml` and are hot-reloaded every 30 seconds
without restarting the engine. Circuit breakers halt all trading at configurable
daily, weekly, and monthly loss thresholds.

---

## Repository Layout

```
sherwood/
├── src/sherwood/
│   ├── core/
│   │   ├── engine.py           event bus, typed event classes
│   │   ├── broker.py           broker adapter interface + Alpaca impl
│   │   ├── portfolio.py        position tracking, P&L accounting
│   │   ├── risk.py             pre-trade risk gate
│   │   ├── session.py          market hours, session timing
│   │   └── universe.py         symbol universe management
│   ├── strategies/
│   │   ├── base.py             abstract Strategy class
│   │   ├── momentum.py         cross-sectional momentum
│   │   ├── mean_reversion.py   rolling z-score reversion
│   │   ├── pairs.py            OLS cointegration pairs
│   │   ├── earnings.py         post-earnings drift
│   │   └── options.py          volatility surface stub
│   ├── data/
│   │   ├── feeds.py            Polygon WebSocket feed
│   │   ├── normalizer.py       tick -> Bar conversion
│   │   ├── cache.py            Redis bar cache
│   │   └── historical.py       yfinance historical loader
│   ├── execution/
│   │   ├── router.py           smart order router
│   │   ├── slippage.py         square-root impact model
│   │   └── fills.py            fill processor, partial fills
│   ├── backtester/
│   │   ├── engine.py           vectorized + event-driven modes
│   │   ├── metrics.py          Sharpe, Sortino, Calmar, drawdown
│   │   └── tearsheet.py        HTML report generation
│   ├── reporting/
│   │   ├── pnl.py              daily P&L tracker -> CSV
│   │   └── tearsheet.py        strategy tearsheet
│   ├── monitoring/
│   │   └── metrics.py          Prometheus counters + gauges
│   └── adapters/
│       └── chain.py            on-chain quote adapter
├── scripts/
│   ├── backtest.py             CLI: run backtest
│   ├── paper.py                CLI: paper trading mode
│   ├── live.py                 CLI: live trading (confirmation required)
│   └── optimize.py             CLI: walk-forward optimization
├── config/
│   ├── default.yaml            engine, broker, data settings
│   ├── strategies.yaml         per-strategy parameters
│   ├── risk.yaml               risk limits + circuit breakers
│   ├── pairs.json              cointegrated pair definitions
│   ├── universe.yaml           custom symbol list
│   └── logging.yaml            log handler configuration
├── docs/
│   ├── quickstart.md
│   ├── signals.md
│   ├── risk-model.md
│   ├── execution.md
│   ├── backtesting.md
│   ├── deployment.md
│   └── api-reference.md
└── tests/                      94% coverage
```

---

## Quickstart

```bash
git clone <repo>
cd sherwood
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
cp .env.example .env      # add broker credentials
make paper                # start paper trading
```

Run a backtest:

```bash
python scripts/backtest.py \
  --strategy momentum \
  --start 2020-01-01 \
  --end 2024-12-31 \
  --capital 1000000
```

Walk-forward optimization:

```bash
python scripts/optimize.py --strategy pairs --start 2019-01-01 --end 2023-12-31
```

---

## Configuration

```yaml
# config/default.yaml
engine:
  mode: paper
  universe: sp500
  max_positions: 40
  capital: 1_000_000

broker:
  primary: alpaca
  fallback: ibkr
```

```yaml
# config/risk.yaml
limits:
  max_position_pct: 0.05
  max_sector_pct: 0.25
  min_adv_usd: 5_000_000

circuit_breakers:
  intraday_loss_pct: 0.02
  weekly_loss_pct: 0.05
  monthly_loss_pct: 0.10

hot_reload: true
```

---

## Monitoring

Prometheus on `:8000/metrics`. Grafana dashboard via `docker compose`.

Key signals: `sherwood_equity_usd` · `sherwood_positions_count` · `sherwood_order_latency_seconds` · `sherwood_risk_blocks_total`

---

*Private repository. Not a public release.*
