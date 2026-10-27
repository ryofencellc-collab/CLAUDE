"""Round 13 stress audit (diagnostics only; the verdict in ROUND13.md stands as pre-registered).

Checks whether the pass survives: higher costs, removing its best year, each era on its own,
shifted refit dates, and the fixed final config without walk-forward re-selection.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round13
from edge.stats import deflated_sharpe
from run_round9b import download


def stats(r: pd.Series) -> dict:
    r = r.dropna()
    eq = (1 + r).cumprod()
    yrs = len(r) / 252
    return dict(sharpe=r.mean() / r.std() * np.sqrt(252), cagr=eq.iloc[-1] ** (1 / yrs) - 1,
                mdd=(eq / eq.cummax() - 1).min(), usd=1000 * eq.iloc[-1], dsr=deflated_sharpe(r, 269, 1 / len(r)))


def row(name, r, spy):
    s, b = stats(r), stats(spy.reindex(r.index).fillna(0))
    return (f"| {name} | {s['sharpe']:.2f} | {b['sharpe']:.2f} | {s['cagr']:+.1%} | {b['cagr']:+.1%} | "
            f"{s['mdd']:.1%} | ${s['usd']:,.0f} | {s['dsr']:.3f} |")


def main():
    close = download(round13.ASSETS)
    px = close[round13.ASSETS].dropna(subset=["SPY"])
    spy = px["SPY"].pct_change(fill_method=None)
    base, _, _ = round13.walk_forward(px)
    lines = ["# Round 13 stress audit", "",
             "Diagnostics only: the pre-registered verdict in [ROUND13.md](ROUND13.md) stands either way.", "",
             "| Variant | Sharpe | SPY Sharpe | CAGR | SPY CAGR | Worst drop | $1,000 → | Deflated Sharpe |",
             "|---|---:|---:|---:|---:|---:|---:|---:|", row("As tested", base, spy)]
    orig = dict(round13.COSTS)
    for k in (2, 3):
        round13.COSTS.update({a: c * k for a, c in orig.items()})
        r, _, _ = round13.walk_forward(px)
        lines.append(row(f"Costs x{k}", r, spy))
    round13.COSTS.update(orig)
    lines.append(row("Without 2017", base[base.index.year != 2017], spy))
    lines.append(row("Without 2017 and 2020", base[~base.index.year.isin([2017, 2020])], spy))
    for a, b in (("2012", "2016"), ("2017", "2021"), ("2022", "2026")):
        lines.append(row(f"Only {a}-{b}", base[a:b], spy))
    first = round13.FIRST_TEST
    for m in (3,):
        round13.FIRST_TEST = first + pd.DateOffset(months=m)
        r, _, _ = round13.walk_forward(px)
        lines.append(row(f"Refits shifted {m} months", r, spy))
    round13.FIRST_TEST = first
    trend_w = round13.round11.weights(px[round13.ETFS], round13.TREND_CFG)
    sleeves = {n: round13.crypto_sleeve(px, n) for n in (50, 100)}
    for cid in ("volman-sma50-crypto30-trend40", "volman-sma100-crypto30-trend40", "hold-sma50-crypto10-trend20"):
        core, sma, a, b = cid.split("-")
        c = dict(core=core, sma=int(sma[3:]), alpha=int(a[6:]) / 100, beta=int(b[5:]) / 100)
        net, _ = round13.backtest(round13.combine(px, c, trend_w, sleeves), px)
        lines.append(row(f"Fixed {cid}, 2012+", net[net.index >= first], spy))
    corr = pd.DataFrame({"strategy": base, "SPY": spy.reindex(base.index)}).corr().iloc[0, 1]
    lines += ["", f"Daily correlation with SPY: {corr:.2f}."]
    Path("reports/ROUND13_ROBUST.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
