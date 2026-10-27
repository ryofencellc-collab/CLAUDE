"""Round 9 runner (PROTOCOL_ROUND9.md): data-chosen trade gates, judged walk-forward.

    python run_round9.py            # full: 30 coins
    R9_SMALL=1 python run_round9.py # smoke: 3 coins, proves the pipeline in minutes
"""
import json
import os
from pathlib import Path

import pandas as pd

from edge import data, gates
from edge.backtest import metrics

SMALL = os.environ.get("R9_SMALL") == "1"
REPORTS = Path("reports")


def main():
    if SMALL:
        data.CRYPTO_UNIVERSE[:] = ["BTC", "ETH", "SOL"]
    p = data.crypto_panel(refresh=True)
    spy = data.etf_panel(refresh=True)["close"]["SPY"]
    print(f"panel: {p['spot_close'].shape[1]} coins, {p['spot_close'].index[0].date()} to "
          f"{p['spot_close'].index[-1].date()}", flush=True)
    oos, turn, log = gates.walk_forward(p, spy)
    v = gates.verdict(oos, turn, p["spot_close"]["BTC"])
    btc = metrics(p["spot_close"]["BTC"].pct_change(fill_method=None).reindex(oos.index).fillna(0), gates.PERIODS)
    eq = (1 + oos).cumprod()
    name = "ROUND9_SMOKE.md" if SMALL else "ROUND9.md"
    lines = [f"# Round 9{' SMOKE TEST (3 coins, pipeline check, not a result)' if SMALL else ''}: "
             "data-chosen trade gates", "",
             "Rules: [PROTOCOL_ROUND9.md](../PROTOCOL_ROUND9.md). Out-of-sample = every 6-month block traded with "
             f"gates chosen without it, {oos.index[0].date()} to {oos.index[-1].date()}.", "",
             f"## Verdict: **{'PASS' if v['pass'] else 'FAIL'}**", "",
             "| | Gate strategy | Buy & hold BTC |", "|---|---:|---:|",
             f"| $1,000 became | ${1000 * eq.iloc[-1]:,.0f} | ${1000 * (1 + btc['total']):,.0f} |",
             f"| Yearly return | {v['cagr']:+.1%} | {btc['cagr']:+.1%} |",
             f"| Sharpe | {v['sharpe']:.2f} | {btc['sharpe']:.2f} |",
             f"| Worst drop | {v['max_dd']:.1%} | {btc['max_dd']:.1%} |",
             f"| Deflated Sharpe (264 trials) | {v['dsr']:.3f} | |",
             f"| Days with a position change | {v['trades']} | |", "",
             "| Check | Result |", "|---|---|"] + \
            [f"| {k} | {'yes' if ok else '**no**'} |" for k, ok in v["checks"].items()] + \
            ["", "## What the data chose at each refit", "",
             "| Refit | # gates | Gates | Validation Sharpe by # gates (0, 1, 2, ...) |", "|---|---:|---|---|"] + \
            [f"| {r['refit']} | {len(r['gates'])} | {', '.join(r['gates']) or '(none: hold all)'} | "
             f"{r['val_sharpe_by_k']} |" for r in log]
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / name).write_text("\n".join(lines) + "\n")
    (REPORTS / name.replace(".md", "_refits.json")).write_text(json.dumps(log, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
