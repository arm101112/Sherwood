# API Reference

## Engine

```python
from sherwood.core.engine import Engine

engine = Engine(config)
engine.start()
engine.stop()
engine.bus.subscribe(SignalEvent, my_handler)
engine.bus.publish(OrderEvent(...))
```

## Strategy

```python
from sherwood.strategies.base import Strategy
from sherwood.core.engine import SignalEvent
import pandas as pd

class MyStrategy(Strategy):
    name = "my_strategy"

    def generate_signals(self, data: pd.DataFrame) -> list[SignalEvent]:
        # data: DataFrame of close prices, columns=symbols, index=dates
        signals = []
        # ... your logic ...
        return signals
```

## Portfolio

```python
from sherwood.core.portfolio import Portfolio

portfolio = Portfolio(initial_capital=1_000_000)
portfolio.apply_fill("AAPL", qty=100, price=150.0, side="buy")
portfolio.update_price("AAPL", 155.0)
snap = portfolio.snapshot()
print(snap.equity)
```

## Risk Gate

```python
from sherwood.core.risk import RiskGate, RiskConfig
from sherwood.core.engine import OrderEvent

config = RiskConfig(max_position_pct=0.05, intraday_loss_pct=0.02)
gate = RiskGate(config)
gate.set_equity(1_000_000)

order = OrderEvent(symbol="AAPL", qty=100, side="buy",
                   order_type="market", limit_price=150.0)
result = gate.evaluate(order, portfolio_snapshot)
# result.decision: "PASS" | "BLOCK" | "REDUCE"
```

## Backtester

```python
from sherwood.backtester.engine import Backtester
from sherwood.backtester.metrics import compute_metrics
from sherwood.strategies.momentum import MomentumStrategy
import pandas as pd

data = pd.DataFrame(...)  # close prices
strategy = MomentumStrategy({"lookback": 252, "top_n": 20})
bt = Backtester(strategy, capital=1_000_000)
result = bt.run(data, start="2020-01-01", end="2024-12-31")
metrics = compute_metrics(result.returns)
```
