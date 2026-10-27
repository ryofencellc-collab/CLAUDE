"""Round 11 runner (PROTOCOL_ROUND13.md): multi-asset trend with risk balancing."""
import json
from pathlib import Path

from edge import gates, round13
from edge.backtest import metrics
from run_round9b import download

REPORTS = Path("reports")


def main():
    close = download(round13.ASSETS)
    px = close[round13.ASSETS].dropna(subset=["SPY"])
    print(f"assets {px.shape[1]}, {px.index[0].date()} to {px.index[-1].date()}; "
          f"BTC from {px['BTC-USD'].first_valid_index().date()}, ETH from {px['ETH-USD'].first_valid_index().date()}",
          flush=True)
    oos, turn, log = round13.walk_forward(px)
    v = gates.verdict(oos, turn, px["SPY"], 269, 252)
    b = metrics(px["SPY"].pct_change(fill_method=None).reindex(oos.index).fillna(0), 252)
    eq = (1 + oos).cumprod()
    yearly = (1 + oos).groupby(oos.index.year).prod() - 1
    lines = ["# Round 13: stock core + multi-asset trend + crypto trend", "",
             f"Rules: [PROTOCOL_ROUND13.md](../PROTOCOL_ROUND13.md). Out-of-sample {oos.index[0].date()} to "
             f"{oos.index[-1].date()}; config re-chosen every 6 months from past data only.", "",
             f"## Verdict: **{'PASS' if v['pass'] else 'FAIL'}**", "",
             "| | Strategy | Buy & hold SPY |", "|---|---:|---:|",
             f"| $1,000 became | ${1000 * eq.iloc[-1]:,.0f} | ${1000 * (1 + b['total']):,.0f} |",
             f"| Yearly return | {v['cagr']:+.1%} | {b['cagr']:+.1%} |",
             f"| Sharpe | {v['sharpe']:.2f} | {b['sharpe']:.2f} |",
             f"| Worst drop | {v['max_dd']:.1%} | {b['max_dd']:.1%} |",
             f"| Deflated Sharpe (269 trials) | {v['dsr']:.3f} | |", "",
             "| Check | Result |", "|---|---|"] + \
            [f"| {k} | {'yes' if ok else '**no**'} |" for k, ok in v["checks"].items()] + \
            ["", "## Config chosen at each refit", "", "| Refit | Chosen | Training Sharpe |", "|---|---|---:|"] + \
            [f"| {r['refit']} | {r['chosen']} | {r['train_sharpe']} |" for r in log] + \
            ["", "## By year (out of sample)", "", "| Year | Return |", "|---|---:|"] + \
            [f"| {y} | {r:+.1%} |" for y, r in yearly.items()]
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "ROUND13.md").write_text("\n".join(lines) + "\n")
    (REPORTS / "ROUND13_refits.json").write_text(json.dumps(log, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
