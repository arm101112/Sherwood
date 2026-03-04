import pytest

from sherwood.core.engine import OrderEvent
from sherwood.core.risk import RiskGate, RiskConfig


def make_order(symbol="AAPL", qty=100, price=150.0, side="buy") -> OrderEvent:
    return OrderEvent(symbol=symbol, qty=qty, side=side,
                      order_type="market", limit_price=price)


def test_risk_pass_normal_order():
    gate = RiskGate(RiskConfig(max_position_pct=0.05))
    gate.set_equity(1_000_000)
    gate.update_pnl(0.0)
    order = make_order(qty=30, price=150.0)
    result = gate.evaluate(order, None)
    assert result.decision == "PASS"


def test_risk_blocks_on_drawdown():
    gate = RiskGate(RiskConfig(intraday_loss_pct=0.02))
    gate.set_equity(1_000_000)
    gate.update_pnl(-25_000)
    order = make_order()
    result = gate.evaluate(order, None)
    assert result.decision == "BLOCK"
    assert "drawdown" in result.reason


def test_risk_reduces_oversized_order():
    gate = RiskGate(RiskConfig(max_position_pct=0.05))
    gate.set_equity(1_000_000)
    gate.update_pnl(0)
    order = make_order(qty=1000, price=200.0)
    result = gate.evaluate(order, None)
    assert result.decision == "REDUCE"
    assert result.adjusted_qty is not None
    assert result.adjusted_qty < 1000


def test_slippage_model():
    from sherwood.execution.slippage import SlippageModel
    model = SlippageModel(bps=2.0)
    buy_price = model.adjust(100.0, "buy", 100)
    sell_price = model.adjust(100.0, "sell", 100)
    assert buy_price > 100.0
    assert sell_price < 100.0
