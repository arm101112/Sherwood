from __future__ import annotations

import threading
from typing import Any

try:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class MetricsServer:
    def __init__(self, port: int = 8000) -> None:
        self._port = port
        self._started = False

        if not PROMETHEUS_AVAILABLE:
            return

        self.orders_submitted = Counter(
            "sherwood_orders_submitted_total",
            "Total orders submitted",
            ["strategy", "side", "venue"],
        )
        self.fills_received = Counter(
            "sherwood_fills_received_total",
            "Total fills received",
            ["strategy", "side"],
        )
        self.signals_generated = Counter(
            "sherwood_signals_generated_total",
            "Total signals generated",
            ["strategy", "direction"],
        )
        self.risk_blocks = Counter(
            "sherwood_risk_blocks_total",
            "Orders blocked by risk gate",
            ["reason"],
        )
        self.equity = Gauge(
            "sherwood_equity_usd",
            "Current portfolio equity in USD",
        )
        self.cash = Gauge(
            "sherwood_cash_usd",
            "Current cash balance in USD",
        )
        self.num_positions = Gauge(
            "sherwood_positions_count",
            "Number of open positions",
        )
        self.order_latency = Histogram(
            "sherwood_order_latency_seconds",
            "Order submission latency",
            buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1],
        )

    def start(self) -> None:
        if not PROMETHEUS_AVAILABLE or self._started:
            return
        start_http_server(self._port)
        self._started = True
