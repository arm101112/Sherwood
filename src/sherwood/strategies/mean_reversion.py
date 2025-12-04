from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from sherwood.core.engine import SignalEvent
from sherwood.strategies.base import Strategy


class MeanReversionStrategy(Strategy):
    name = "mean_reversion"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.lookback: int = config.get("lookback", 20)
        self.entry_z: float = config.get("zscore_entry", 2.0)
        self.exit_z: float = config.get("zscore_exit", 0.5)

    def _zscore(self, series: pd.Series) -> pd.Series:
        roll = series.rolling(self.lookback)
        return (series - roll.mean()) / roll.std()

    def generate_signals(self, data: pd.DataFrame) -> list[SignalEvent]:
        signals: list[SignalEvent] = []
        for symbol in data.columns:
            prices = data[symbol].dropna()
            if len(prices) < self.lookback + 1:
                continue

            z = self._zscore(prices).iloc[-1]
            if np.isnan(z):
                continue

            if z < -self.entry_z:
                signals.append(SignalEvent(
                    strategy=self.name,
                    symbol=symbol,
                    direction=1,
                    confidence=min(abs(z) / self.entry_z, 1.0),
                    metadata={"zscore": z},
                ))
            elif z > self.entry_z:
                signals.append(SignalEvent(
                    strategy=self.name,
                    symbol=symbol,
                    direction=-1,
                    confidence=min(abs(z) / self.entry_z, 1.0),
                    metadata={"zscore": z},
                ))

        return signals
