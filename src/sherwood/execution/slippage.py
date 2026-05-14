from __future__ import annotations

import math


class SlippageModel:
    def __init__(self, bps: float = 2.0, market_impact_coeff: float = 0.1) -> None:
        self._bps = bps / 10_000
        self._impact = market_impact_coeff

    def adjust(self, price: float, side: str, qty: int,
               adv: float | None = None) -> float:
        slip = price * self._bps
        if adv and adv > 0:
            participation = qty * price / adv
            slip += price * self._impact * math.sqrt(participation)
        return price + slip if side == "buy" else price - slip

    def expected_cost(self, price: float, qty: int, adv: float | None = None) -> float:
        adj = self.adjust(price, "buy", qty, adv)
        return abs(adj - price) * qty

