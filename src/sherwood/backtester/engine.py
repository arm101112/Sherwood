from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from structlog import get_logger

from sherwood.core.engine import OrderEvent, FillEvent
from sherwood.core.portfolio import Portfolio
from sherwood.core.risk import RiskGate, RiskConfig
from sherwood.execution.slippage import SlippageModel
from sherwood.strategies.base import Strategy

log = get_logger(__name__)


@dataclass
class BacktestResult:
    returns: pd.Series
    equity_curve: pd.Series
    trades: list[dict] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)


class Backtester:
    def __init__(self, strategy: Strategy, capital: float = 1_000_000,
                 commission_bps: float = 1.0,
                 slippage: SlippageModel | None = None) -> None:
        self._strategy = strategy
        self._capital = capital
        self._commission_bps = commission_bps / 10_000
        self._slippage = slippage or SlippageModel()

    def run(self, data: pd.DataFrame,
            start: str | None = None,
            end: str | None = None) -> BacktestResult:
        if start:
            data = data[data.index >= start]
        if end:
            data = data[data.index <= end]

        portfolio = Portfolio(self._capital)
        risk = RiskGate(RiskConfig())
        risk.set_equity(self._capital)

        equity_curve: list[float] = []
        trades: list[dict] = []

        for i in range(1, len(data)):
            window = data.iloc[: i + 1]
            signals = self._strategy.generate_signals(window)

            for sig in signals:
                if sig.symbol not in data.columns:
                    continue
                price = window[sig.symbol].iloc[-1]
                if np.isnan(price) or price <= 0:
                    continue

                notional = portfolio.equity * 0.02 * sig.confidence
                qty = max(1, int(notional / price))
                side = "buy" if sig.direction == 1 else "sell"

                order = OrderEvent(symbol=sig.symbol, qty=qty, side=side,
                                   order_type="market", limit_price=price,
                                   strategy=sig.strategy)
                risk_result = risk.evaluate(order, None)

                if risk_result.decision == "BLOCK":
                    continue

                final_qty = risk_result.adjusted_qty or qty
                fill_price = self._slippage.adjust(price, side, final_qty)
                commission = fill_price * final_qty * self._commission_bps

                portfolio.apply_fill(sig.symbol, final_qty, fill_price,
                                     side, commission)
                trades.append({"date": window.index[-1], "symbol": sig.symbol,
                                "qty": final_qty, "price": fill_price, "side": side})

            equity_curve.append(portfolio.equity)
            risk.set_equity(portfolio.equity)
            risk.update_pnl(portfolio.equity - self._capital)

        eq = pd.Series(equity_curve, index=data.index[1:])
        returns = eq.pct_change().dropna()

        return BacktestResult(returns=returns, equity_curve=eq, trades=trades)
