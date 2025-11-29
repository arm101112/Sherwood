from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from sherwood.core.engine import SignalEvent
from sherwood.strategies.base import Strategy


class MomentumStrategy(Strategy):
    name = "momentum"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.lookback: int = config.get("lookback", 252)
        self.top_n: int = config.get("top_n", 20)
        self.max_weight: float = config.get("max_weight", 0.1)

    def generate_signals(self, data: pd.DataFrame) -> list[SignalEvent]:
        if len(data) < self.lookback:
            return []

        returns = data.pct_change(self.lookback).iloc[-1].dropna()
        returns = returns.replace([np.inf, -np.inf], np.nan).dropna()

        top = returns.nlargest(self.top_n)
        bottom = returns.nsmallest(self.top_n // 4)

        signals: list[SignalEvent] = []

        for symbol, ret in top.items():
            confidence = float(np.clip(ret / returns.std(), 0, 3) / 3)
            signals.append(SignalEvent(
                strategy=self.name,
                symbol=str(symbol),
                direction=1,
                confidence=confidence,
                metadata={"momentum_return": ret},
            ))

        for symbol, ret in bottom.items():
            signals.append(SignalEvent(
                strategy=self.name,
                symbol=str(symbol),
                direction=-1,
                confidence=0.5,
                metadata={"momentum_return": ret},
            ))

        return signals
