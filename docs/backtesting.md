# Backtesting

## Engine Modes

**Vectorized mode** (default): signal generation and portfolio simulation run
over the full dataset in a single pass. Fast, suitable for parameter sweeps.

**Event-driven mode**: simulates the production event loop tick-by-tick.
Slower, but faithfully reproduces execution timing and latency effects.

## Walk-Forward Optimization

```
sherwood optimize --strategy pairs \
  --param entry_spread_z 1.5,2.0,2.5 \
  --param exit_spread_z 0.2,0.5 \
  --train-window 252 \
  --test-window 63 \
  --output reports/wfo.json
```

Each window trains on `train-window` trading days and tests on the next
`test-window` days. Parameters are selected by in-sample Sharpe and
evaluated on out-of-sample returns. Avoids overfitting by never touching
the test window during optimization.

## Monte Carlo Analysis

Randomizes trade order and entry timing (1,000–10,000 paths) to estimate
the distribution of drawdowns for a given strategy. Output includes:

- Expected max drawdown (median of paths)
- 95th percentile drawdown
- Probability of drawdown exceeding configurable threshold

## Point-in-Time Data

All backtests use point-in-time data to avoid lookahead bias. Financial
statement data is lagged by the filing date, not the report date.
Price data uses the closing price of the signal generation day, with
fills simulated at next-day open + slippage.
