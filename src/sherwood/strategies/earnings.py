from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

from sherwood.core.engine import SignalEvent
from sherwood.strategies.base import Strategy


@dataclass
class EarningsEvent:
    symbol: str
    report_date: datetime
    eps_estimate: float
    eps_actual: float | None = None

    @property
    def surprise_pct(self) -> float | None:
        if self.eps_actual is None or self.eps_estimate == 0:
            return None
        return (self.eps_actual - self.eps_estimate) / abs(self.eps_estimate)


class EarningsDriftStrategy(Strategy):
    name = "earnings_drift"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.min_surprise: float = config.get("min_surprise_pct", 0.05)
        self.hold_days: int = config.get("hold_days", 5)
        self._pending: list[EarningsEvent] = []
        self._positions: dict[str, int] = {}

    def add_earnings_event(self, event: EarningsEvent) -> None:
        self._pending.append(event)

    def generate_signals(self, data: pd.DataFrame) -> list[SignalEvent]:
        signals: list[SignalEvent] = []
        today = data.index[-1]

        for event in list(self._pending):
            if event.eps_actual is None:
                continue
            if event.symbol not in data.columns:
                continue

            surprise = event.surprise_pct
            if surprise is None:
                continue

            days_since = (today - pd.Timestamp(event.report_date)).days
            if days_since > self.hold_days:
                self._pending.remove(event)
                continue

            if abs(surprise) < self.min_surprise:
                continue

            direction = 1 if surprise > 0 else -1
            confidence = min(abs(surprise) / (self.min_surprise * 3), 1.0)

            signals.append(SignalEvent(
                strategy=self.name,
                symbol=event.symbol,
                direction=direction,
                confidence=confidence,
                metadata={
                    "surprise_pct": surprise,
                    "eps_estimate": event.eps_estimate,
                    "eps_actual": event.eps_actual,
                    "days_since_report": days_since,
                },
            ))

        return signals
