from __future__ import annotations

import asyncio
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Type

from structlog import get_logger

log = get_logger(__name__)


@dataclass
class Event:
    pass


@dataclass
class TickEvent(Event):
    symbol: str
    price: float
    volume: int
    timestamp: float


@dataclass
class SignalEvent(Event):
    strategy: str
    symbol: str
    direction: int  # 1 long, -1 short, 0 flat
    confidence: float
    metadata: dict = field(default_factory=dict)


@dataclass
class OrderEvent(Event):
    symbol: str
    qty: int
    side: str  # buy | sell
    order_type: str  # market | limit | vwap | twap
    limit_price: float | None = None
    strategy: str = ""


@dataclass
class FillEvent(Event):
    order_id: str
    symbol: str
    qty: int
    avg_price: float
    side: str
    timestamp: float
    commission: float = 0.0


@dataclass
class RiskEvent(Event):
    order: OrderEvent
    decision: str  # PASS | BLOCK | REDUCE
    reason: str = ""
    adjusted_qty: int | None = None


class EventBus:
    _handlers: dict[Type[Event], list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[Event], handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._handlers[type(event)]:
            try:
                handler(event)
            except Exception:
                log.exception("handler_error", event=type(event).__name__)


class Engine:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.bus = EventBus()
        self._running = False
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self) -> None:
        self._running = True
        self._loop = asyncio.new_event_loop()
        t = threading.Thread(target=self._loop.run_forever, daemon=True)
        t.start()
        log.info("engine_started", mode=self.config.get("engine", {}).get("mode"))

    def stop(self) -> None:
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        log.info("engine_stopped")
