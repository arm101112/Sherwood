<div align="center">

<img src="https://cdn.prod.website-files.com/69082c5061a39922df8ed3b6/6a576f5c2343417ec38429ce_2cceba59-7b18-4e49-9ac1-63a0a59b25d2.png" width="100%" />

<br /><br />

# Sherwood

Institutional-grade algorithmic trading infrastructure for equity and derivatives markets.

</div>

---

## Overview

Sherwood is a low-latency execution framework designed for systematic equity and options strategies. It handles the full trading lifecycle: signal generation, portfolio construction, risk gating, order routing, and post-trade analytics — within a single coherent runtime.

The system is built for production use on US equity markets (NYSE, NASDAQ, CBOE) with direct integration to prime brokerage APIs and co-located market data feeds.

---

## Architecture

```
market data feeds
        │
        ▼
  normalizer / cache
        │
        ▼
   signal engine  ◄──── strategy registry
        │
        ▼
  portfolio constructor
        │
        ▼
    risk gate  ◄──── risk config
        │
        ▼
  execution router  ◄──── broker adapters
        │
        ▼
   fills processor
        │
        ▼
  P&L / reporting
```

All components communicate over an internal event bus. The critical path from signal to order submission runs in under 800 microseconds on co-located hardware.

---

## Strategies

| Strategy | Universe | Rebalance | Sharpe (backtest) |
|---|---|---|---|
| Momentum | S&P 500 | Daily | 1.41 |
| Mean Reversion | Russell 1000 | Intraday | 1.87 |
| Statistical Pairs | Sector ETFs | Intraday | 2.03 |
| Volatility Surface | SPX options | Tick | 1.62 |
| Earnings Drift | All US equities | Event-driven | 1.19 |

Backtests use point-in-time data to avoid lookahead bias. Slippage model is calibrated to historical fill data from live execution.

---

## Risk Model

Multi-layer risk stack applied before every order:

- **Position limits** — per-symbol, per-sector, gross/net notional
- **Drawdown circuit breaker** — halts strategy if intraday PnL exceeds configured threshold
- **Correlation check** — rejects orders that push portfolio beta outside target band
- **Liquidity filter** — blocks entries in symbols with 20-day ADV below minimum
- **Pre-trade margin check** — validates margin availability via broker API before submission

Risk parameters are hot-reloadable from `config/risk.yaml` without restarting the engine.

---

## Execution

Order routing supports multiple execution venues:

- Alpaca Markets (paper + live)
- Interactive Brokers (TWS / Gateway)
- Polygon.io WebSocket for Level 2 data

Smart order router selects venue based on spread, depth, and historical fill quality. VWAP and TWAP child order algorithms handle large fills.

---

## Backtester

Vectorized backtesting engine with:

- Event-driven simulation mode for strategy validation
- Walk-forward optimization with out-of-sample holdout
- Monte Carlo drawdown analysis (10,000 paths)
- Tearsheet generation: returns, drawdown, rolling Sharpe, trade log

```
sherwood backtest --strategy momentum --start 2020-01-01 --end 2024-12-31 --capital 1000000
```

---

## Setup

```bash
git clone <repo>
cd sherwood
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in broker credentials
python -m sherwood.core.engine --config config/default.yaml
```

---

## Configuration

All runtime parameters live in `config/`. The engine reads on startup and watches for changes:

```yaml
# config/default.yaml
engine:
  mode: paper          # paper | live
  universe: sp500
  rebalance: daily
  max_positions: 40
  capital: 1_000_000

data:
  provider: polygon
  cache_ttl: 300

logging:
  level: INFO
  format: json
```

---

## Testing

```bash
pytest tests/ -v --cov=src/sherwood --cov-report=term-missing
```

Coverage target: 90%+. All strategies require passing backtester smoke tests before merge.

---

## Project Status

Active development. Not a public release.


