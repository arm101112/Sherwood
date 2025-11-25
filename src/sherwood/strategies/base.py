from __future__ import annotations

import abc
from typing import Any

import pandas as pd

from sherwood.core.engine import SignalEvent


class Strategy(abc.ABC):
    name: str = "base"

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.enabled: bool = config.get("enabled", True)

    @abc.abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> list[SignalEvent]: ...

    def on_fill(self, symbol: str, qty: int, price: float, side: str) -> None:
        pass

    def on_session_open(self) -> None:
        pass

    def on_session_close(self) -> None:
        pass
