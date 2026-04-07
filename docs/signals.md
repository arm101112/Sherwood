# Signal Reference

All strategies emit `SignalEvent` objects with the following fields:

| Field | Type | Description |
|---|---|---|
| `strategy` | str | Strategy name |
| `symbol` | str | Ticker symbol |
| `direction` | int | 1 = long, -1 = short, 0 = flat/close |
| `confidence` | float | 0.0–1.0 signal strength |
| `metadata` | dict | Strategy-specific context |

## Position Sizing

The portfolio constructor converts signal confidence into position size:

```
notional = portfolio_equity * base_position_pct * confidence
qty = floor(notional / current_price)
```

`base_position_pct` defaults to 2% per signal. Maximum position after
risk gating is capped at `config.risk.max_position_pct` (default 5%).

## Signal Stacking

When multiple strategies emit conflicting signals on the same symbol,
the portfolio constructor applies a weighted average of directions,
weighted by confidence. Net direction below 0.3 is treated as flat.
