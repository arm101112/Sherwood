from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(returns: pd.Series,
                    risk_free: float = 0.05) -> dict[str, float]:
    ann_factor = 252
    excess = returns - risk_free / ann_factor

    ann_return = float((1 + returns.mean()) ** ann_factor - 1)
    ann_vol = float(returns.std() * np.sqrt(ann_factor))
    sharpe = float(excess.mean() / returns.std() * np.sqrt(ann_factor)) \
        if returns.std() > 0 else 0.0

    cum = (1 + returns).cumprod()
    roll_max = cum.cummax()
    drawdown = (cum - roll_max) / roll_max
    max_dd = float(drawdown.min())

    downside = returns[returns < 0].std() * np.sqrt(ann_factor)
    sortino = float(excess.mean() * ann_factor / downside) if downside > 0 else 0.0

    calmar = ann_return / abs(max_dd) if max_dd != 0 else 0.0

    wins = returns[returns > 0]
    losses = returns[returns < 0]
    win_rate = len(wins) / max(len(returns), 1)
    profit_factor = float(wins.sum() / abs(losses.sum())) if len(losses) > 0 else 0.0

    return {
        "annualized_return": ann_return,
        "annualized_volatility": ann_vol,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "calmar_ratio": calmar,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "total_trades": len(returns),
    }

