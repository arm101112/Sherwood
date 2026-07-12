from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import yaml


UniverseType = Literal["sp500", "russell1000", "nasdaq100", "custom"]


SP500_SAMPLE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK.B", "LLY",
    "AVGO", "TSLA", "WMT", "JPM", "V", "MA", "XOM", "UNH", "ORCL",
    "COST", "HD", "PG", "JNJ", "ABBV", "BAC", "MRK", "CVX", "NFLX",
    "CRM", "AMD", "KO", "PEP", "CSCO", "ACN", "TMO", "MCD", "LIN",
    "ABT", "NKE", "TXN", "ADBE", "PM", "DHR", "WFC", "NEE", "AMGN",
    "IBM", "RTX", "SPGI", "GE", "CAT", "BKNG",
]

NASDAQ100_SAMPLE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO",
    "ASML", "ADBE", "COST", "AMD", "NFLX", "PEP", "CSCO", "INTC",
    "QCOM", "INTU", "CMCSA", "TXN", "HON", "AMAT", "SBUX", "ISRG",
    "MU", "LRCX", "REGN", "MDLZ", "KLAC", "PANW",
]


def get_universe(universe_type: UniverseType,
                 config_path: str = "config/universe.yaml") -> list[str]:
    if universe_type == "custom":
        p = Path(config_path)
        if p.exists():
            data = yaml.safe_load(p.read_text())
            return data.get("symbols", [])
        return []
    if universe_type == "sp500":
        return SP500_SAMPLE
    if universe_type == "nasdaq100":
        return NASDAQ100_SAMPLE
    return SP500_SAMPLE
