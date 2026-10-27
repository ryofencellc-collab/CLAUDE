"""Round 10 runner (PROTOCOL_ROUND10.md). R10_SMALL=1: 3 coins, pipeline check."""
import json
import os
from pathlib import Path

from edge import data, gates, round10
from edge.backtest import metrics

SMALL = os.environ.get("R10_SMALL") == "1"
REPORTS = Path("reports")


def main():
    if SMALL:
        data.CRYPTO_UNIVERSE[:] = ["BTC", "ETH", "SOL"]
    p = data.crypto_panel(refresh=True)
    oos, turn, log = round10.walk_forward(p)
    btc_close = p["spot_close"]["BTC"]
    v = gates.verdict(oos, turn, btc_close, 266, round10.PERIODS)
    b = metrics(btc_close.pct_change(fill_method=None).reindex(oos.index).fillna(0), round10.PERIODS)
    eq = (1 + oos).cumprod()
    name = "ROUND10_SMOKE.md" if SMALL else "ROUND10.md"
    lines = [f"# Round 10{' SMOKE TEST (3 coins, not a result)' if SMALL else ''}: crypto trend + volatility limit", "",
             f"Rules: [PROTOCOL_ROUND10.md](../PROTOCOL_ROUND10.md). Out-of-sample {oos.index[0].date()} to "
             f"{oos.index[-1].date()}; config re-chosen every 6 months from past data only.", "",
             f"## Verdict: **{'PASS' if v['pass'] else 'FAIL'}**", "",
             "| | Strategy | Buy & hold BTC |", "|---|---:|---:|",
             f"| $1,000 became | ${1000 * eq.iloc[-1]:,.0f} | ${1000 * (1 + b['total']):,.0f} |",
             f"| Yearly return | {v['cagr']:+.1%} | {b['cagr']:+.1%} |",
             f"| Sharpe | {v['sharpe']:.2f} | {b['sharpe']:.2f} |",
             f"| Worst drop | {v['max_dd']:.1%} | {b['max_dd']:.1%} |",
             f"| Deflated Sharpe (266 trials) | {v['dsr']:.3f} | |", "",
             "| Check | Result |", "|---|---|"] + \
            [f"| {k} | {'yes' if ok else '**no**'} |" for k, ok in v["checks"].items()] + \
            ["", "## Config chosen at each refit", "", "| Refit | Chosen | Training Sharpe |", "|---|---|---:|"] + \
            [f"| {r['refit']} | {r['chosen']} | {r['train_sharpe']} |" for r in log]
    yearly = (1 + oos).groupby(oos.index.year).prod() - 1
    lines += ["", "## By year (out of sample)", "", "| Year | Return |", "|---|---:|"] + \
             [f"| {y} | {r:+.1%} |" for y, r in yearly.items()]
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / name).write_text("\n".join(lines) + "\n")
    (REPORTS / name.replace(".md", "_refits.json")).write_text(json.dumps(log, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
