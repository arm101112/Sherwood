from __future__ import annotations

import json
import time
from typing import Any

import redis

from sherwood.data.normalizer import Bar


class BarCache:
    def __init__(self, redis_url: str = "redis://localhost:6379/0",
                 ttl: int = 300) -> None:
        self._r = redis.from_url(redis_url, decode_responses=True)
        self._ttl = ttl

    def _key(self, symbol: str) -> str:
        return f"bars:{symbol}"

    def push(self, bar: Bar) -> None:
        key = self._key(bar.symbol)
        self._r.lpush(key, json.dumps({
            "o": bar.open, "h": bar.high, "l": bar.low, "c": bar.close,
            "v": bar.volume, "t": bar.timestamp, "vw": bar.vwap,
        }))
        self._r.ltrim(key, 0, 5 * 390 - 1)  # 5 trading days of 1-min bars
        self._r.expire(key, self._ttl)

    def get_closes(self, symbol: str, n: int = 252) -> list[float]:
        key = self._key(symbol)
        raw = self._r.lrange(key, 0, n - 1)
        return [json.loads(r)["c"] for r in raw]

    def latest_price(self, symbol: str) -> float | None:
        raw = self._r.lindex(self._key(symbol), 0)
        if raw is None:
            return None
        return json.loads(raw)["c"]
