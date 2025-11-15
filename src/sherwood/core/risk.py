from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from structlog import get_logger

from sherwood.core.engine import OrderEvent, RiskEvent

log = get_logger(__name__)


@dataclass
class RiskConfig:
    max_position_pct: float = 0.05
    max_sector_pct: float = 0.25
    max_gross_leverage: float = 1.5
    max_net_leverage: float = 0.8
    min_adv_usd: float = 5_000_000
    intraday_loss_pct: float = 0.02
    weekly_loss_pct: float = 0.05


class RiskGate:
    def __init__(self, config: RiskConfig) -> None:
        self._cfg = config
        self._intraday_pnl: float = 0.0
        self._equity: float = 1.0

    def set_equity(self, equity: float) -> None:
        self._equity = equity

    def update_pnl(self, pnl: float) -> None:
        self._intraday_pnl = pnl

    def evaluate(self, order: OrderEvent, portfolio_snapshot: Any) -> RiskEvent:
        if self._intraday_pnl / self._equity < -self._cfg.intraday_loss_pct:
            return RiskEvent(order=order, decision="BLOCK",
                             reason="intraday_drawdown_exceeded")

        notional = order.qty * (order.limit_price or 0)
        position_pct = notional / max(self._equity, 1)
        if position_pct > self._cfg.max_position_pct:
            max_qty = int(self._equity * self._cfg.max_position_pct /
                          max(order.limit_price or 1, 1))
            log.warning("position_size_reduced", symbol=order.symbol,
                        original=order.qty, reduced=max_qty)
            return RiskEvent(order=order, decision="REDUCE",
                             reason="position_limit", adjusted_qty=max_qty)

        log.debug("risk_pass", symbol=order.symbol, qty=order.qty)
        return RiskEvent(order=order, decision="PASS")
