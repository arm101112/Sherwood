from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

from sherwood.core.engine import SignalEvent
from sherwood.strategies.base import Strategy


class PairsStrategy(Strategy):
    name = "pairs"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.entry_z: float = config.get("entry_spread_z", 2.0)
        self.exit_z: float = config.get("exit_spread_z", 0.25)
        self.stop_z: float = config.get("stop_loss_z", 3.5)
        pairs_file = config.get("pairs_file", "config/pairs.json")
        self.pairs: list[tuple[str, str]] = self._load_pairs(pairs_file)
        self._hedge_ratios: dict[tuple[str, str], float] = {}

    def _load_pairs(self, path: str) -> list[tuple[str, str]]:
        p = Path(path)
        if not p.exists():
            return []
        data = json.loads(p.read_text())
        return [(item["leg1"], item["leg2"]) for item in data.get("pairs", [])]

    def _compute_hedge_ratio(self, y: pd.Series, x: pd.Series) -> float:
        model = OLS(y, add_constant(x)).fit()
        return float(model.params.iloc[1])

    def _spread_zscore(self, y: pd.Series, x: pd.Series, hr: float) -> float:
        spread = y - hr * x
        return float((spread.iloc[-1] - spread.mean()) / (spread.std() + 1e-9))

    def generate_signals(self, data: pd.DataFrame) -> list[SignalEvent]:
        signals: list[SignalEvent] = []

        for leg1, leg2 in self.pairs:
            if leg1 not in data.columns or leg2 not in data.columns:
                continue
            y = data[leg1].dropna()
            x = data[leg2].dropna()
            idx = y.index.intersection(x.index)
            y, x = y[idx], x[idx]
            if len(y) < 60:
                continue

            hr = self._compute_hedge_ratio(y, x)
            self._hedge_ratios[(leg1, leg2)] = hr
            z = self._spread_zscore(y, x, hr)

            if z < -self.entry_z:
                signals.extend([
                    SignalEvent(self.name, leg1, 1, min(abs(z) / self.entry_z, 1.0),
                                {"zscore": z, "pair": leg2}),
                    SignalEvent(self.name, leg2, -1, min(abs(z) / self.entry_z, 1.0),
                                {"zscore": z, "pair": leg1}),
                ])
            elif z > self.entry_z:
                signals.extend([
                    SignalEvent(self.name, leg1, -1, min(abs(z) / self.entry_z, 1.0),
                                {"zscore": z, "pair": leg2}),
                    SignalEvent(self.name, leg2, 1, min(abs(z) / self.entry_z, 1.0),
                                {"zscore": z, "pair": leg1}),
                ])

        return signals

