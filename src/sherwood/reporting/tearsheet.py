from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_tearsheet(result: Any, output_path: str = "reports/tearsheet.html") -> None:
    from sherwood.backtester.metrics import compute_metrics

    metrics = compute_metrics(result.returns)
    equity = result.equity_curve

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    eq_points = list(zip(
        range(len(equity)),
        (equity / equity.iloc[0] * 100).tolist(),
    ))
    path_d = "M " + " L ".join(f"{x},{100 + 100 - y:.1f}" for x, y in eq_points)
    width = len(equity)

    rows = "".join(
        f"<tr><td>{k.replace('_', ' ').title()}</td>"
        f"<td class='val'>{v:+.4f}</td></tr>"
        for k, v in metrics.items()
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
<title>Sherwood Tearsheet</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'SF Mono',monospace;background:#0a0a0a;color:#d0d0d0;padding:48px}}
h1{{font-size:20px;font-weight:500;color:#fff;margin-bottom:32px;letter-spacing:.05em}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:32px}}
.card{{background:#111;border:1px solid #222;border-radius:8px;padding:24px}}
.card h2{{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#555;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse}}
td{{padding:6px 0;font-size:13px;border-bottom:1px solid #1a1a1a}}
td:first-child{{color:#666}}
.val{{text-align:right;color:#e0e0e0;font-variant-numeric:tabular-nums}}
svg{{width:100%;height:200px}}
path{{fill:none;stroke:#4ade80;stroke-width:1.5}}
</style>
</head>
<body>
<h1>Sherwood — Strategy Tearsheet</h1>
<div class="grid">
<div class="card">
<h2>Equity Curve</h2>
<svg viewBox="0 0 {width} 200" preserveAspectRatio="none">
<path d="{path_d}"/>
</svg>
</div>
<div class="card">
<h2>Performance Metrics</h2>
<table>{rows}</table>
</div>
</div>
</body>
</html>"""

    Path(output_path).write_text(html)
