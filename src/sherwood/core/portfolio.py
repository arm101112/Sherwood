from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from structlog import get_logger

log = get_logger(__name__)


@dataclass
class PortfolioSnapshot:
    cash: float
    equity: float
    positions: Dict[str, float]  # symbol -> market value
    pnl_today: float
    pnl_total: float


class Portfolio:
    def __init__(self, initial_capital: float) -> None:
        self._capital = initial_capital
        self._cash = initial_capital
        self._positions: Dict[str, dict] = {}
        self._realized_pnl: float = 0.0
        self._cost_basis: Dict[str, float] = {}

    @property
    def equity(self) -> float:
        return self._cash + sum(
            p["qty"] * p["last_price"] for p in self._positions.values()
        )

    def update_price(self, symbol: str, price: float) -> None:
        if symbol in self._positions:
            self._positions[symbol]["last_price"] = price

    def apply_fill(self, symbol: str, qty: int, price: float, side: str,
                   commission: float = 0.0) -> None:
        signed_qty = qty if side == "buy" else -qty
        cost = signed_qty * price + commission

        if symbol not in self._positions:
            self._positions[symbol] = {"qty": 0, "avg_cost": 0.0, "last_price": price}

        pos = self._positions[symbol]
        if pos["qty"] == 0:
            pos["qty"] = signed_qty
            pos["avg_cost"] = price
        else:
            total_qty = pos["qty"] + signed_qty
            if total_qty == 0:
                pnl = pos["qty"] * (price - pos["avg_cost"]) - commission
                self._realized_pnl += pnl
                del self._positions[symbol]
                return
            pos["avg_cost"] = (
                (pos["qty"] * pos["avg_cost"] + signed_qty * price) / total_qty
            )
            pos["qty"] = total_qty

        self._cash -= cost
        log.info("fill_applied", symbol=symbol, qty=signed_qty, price=price,
                 equity=self.equity)

    def snapshot(self, pnl_today: float = 0.0) -> PortfolioSnapshot:
        return PortfolioSnapshot(
            cash=self._cash,
            equity=self.equity,
            positions={s: p["qty"] * p["last_price"]
                       for s, p in self._positions.items()},
            pnl_today=pnl_today,
            pnl_total=self._realized_pnl,
        )

