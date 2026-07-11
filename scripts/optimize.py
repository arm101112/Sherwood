"""Walk-forward parameter optimization."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sherwood.backtester.engine import Backtester
from sherwood.backtester.metrics import compute_metrics
from sherwood.data.historical import load_universe
from sherwood.strategies import MomentumStrategy, MeanReversionStrategy


def walk_forward(strategy_cls, param_grid: dict, data: pd.DataFrame,
                 train_window: int = 252, test_window: int = 63,
                 capital: float = 1_000_000) -> list[dict]:
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    results = []

    for params in itertools.product(*values):
        cfg = dict(zip(keys, params))
        cfg["enabled"] = True

        out_of_sample_returns = []

        for start in range(0, len(data) - train_window - test_window, test_window):
            train = data.iloc[start: start + train_window]
            test = data.iloc[start + train_window: start + train_window + test_window]

            strategy = strategy_cls(cfg)
            bt_train = Backtester(strategy, capital=capital)
            bt_train.run(train)

            strategy_test = strategy_cls(cfg)
            bt_test = Backtester(strategy_test, capital=capital)
            result = bt_test.run(test)
            out_of_sample_returns.append(result.returns)

        if out_of_sample_returns:
            combined = pd.concat(out_of_sample_returns)
            metrics = compute_metrics(combined)
            results.append({"params": cfg, "metrics": metrics})

    results.sort(key=lambda r: r["metrics"]["sharpe_ratio"], reverse=True)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", default="momentum")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2024-12-31")
    parser.add_argument("--output", default="reports/optimization.json")
    args = parser.parse_args()

    data = load_universe(start=args.start, end=args.end)

    if args.strategy == "momentum":
        grid = {"lookback": [126, 252], "top_n": [10, 20], "max_weight": [0.05, 0.1]}
        cls = MomentumStrategy
    else:
        grid = {"lookback": [10, 20], "zscore_entry": [1.5, 2.0, 2.5]}
        cls = MeanReversionStrategy

    results = walk_forward(cls, grid, data)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results[:10], f, indent=2)

    print(f"Best params: {results[0]['params']}")
    print(f"Best Sharpe: {results[0]['metrics']['sharpe_ratio']:.3f}")


if __name__ == "__main__":
    main()
