"""Round 7 runner (PROTOCOL_ROUND7.md).

    python run_round7.py arb | tennis | funding | pairs
"""
import json
import sys

import numpy as np
import pandas as pd

from edge import round7 as r7
from edge.backtest import metrics
from edge.betting import bootstrap_p
from edge.stats import deflated_sharpe
from run_round2 import REPORTS, fmt

TRIALS = 211


def part_arb():
    from edge import weather as wx
    wdf = wx.dataset()
    arb, info = r7.bracket_arb(wdf)
    lines = ["## 7A. Kalshi bracket arbitrage", "",
             f"Contracts loaded: {len(wdf):,}. Events with every bracket quoted at 09:00 and a clean "
             f"settlement: {info['events_checked']:,} (bad settlements skipped: {info['events_bad_settlement']}).", ""]
    if not len(arb):
        return "\n".join(lines + ["No complete events."])
    lines += [f"Σ ask: median {arb.sum_ask.median():.3f}, min {arb.sum_ask.min():.3f}. "
              f"Σ bid: median {arb.sum_bid.median():.3f}, max {arb.sum_bid.max():.3f}.", ""]
    for side in ("buy_all", "sell_all"):
        o = arb[arb[side] > 0]
        yrs = max((arb["date"].max() - arb["date"].min()).days / 365, 1 / 365)
        lines.append(f"- **{side}**: {len(o)} opportunities of {len(arb)} events; "
                     f"profit per set mean ${o[side].mean() if len(o) else 0:.4f}; "
                     f"total at {r7.ARB_SIZE} sets/opportunity ${o[side].sum() * r7.ARB_SIZE:,.2f} "
                     f"(≈ ${o[side].sum() * r7.ARB_SIZE / yrs:,.0f}/yr). "
                     f"**{'PASS' if len(o) >= 30 and o[side].sum() > 0 else 'FAIL'}**")
        if len(o):
            top = o.nlargest(10, side)[["event", "brackets", "sum_ask", "sum_bid", side]]
            lines += ["", fmt(top), ""]
    return "\n".join(lines)


def part_tennis():
    df = r7.tennis(refresh=True)
    rows = []
    for params in r7.TENNIS_GRID:
        b = r7.tennis_value(df, **params)
        is_b, ho = b[b["year"] < 2022], b[b["year"] >= 2022]
        rows.append(dict(params=json.dumps(params), is_bets=len(is_b), is_roi=is_b["ret"].mean(),
                         oos_bets=len(ho), oos_roi=ho["ret"].mean(), oos_win_rate=(ho["ret"] > 0).mean(),
                         oos_profit_at_10=ho["ret"].sum() * 10, oos_p=bootstrap_p(ho["ret"])))
    t = pd.DataFrame(rows)
    b = t.loc[t["is_roi"].idxmax()]
    p_adj = min(1.0, b["oos_p"] * TRIALS)
    ok = b["oos_roi"] > 0 and p_adj < 0.05 and b["is_roi"] > 0 and b["oos_bets"] >= 1000
    per_year = r7.tennis_value(df, **json.loads(b["params"])).groupby("year")["ret"].agg(["size", "mean"])
    return "\n".join(["## 7B. Tennis value betting", "",
                      f"Matches: {len(df):,} ({df['year'].min()}–{df['year'].max()}, ATP+WTA).", "",
                      f"Selected {b['params']}: holdout ROI {b['oos_roi']:+.2%} on {b['oos_bets']} bets, "
                      f"p_adj {p_adj:.3f} → **{'PASS' if ok else 'FAIL'}**", "", fmt(t), "",
                      "Selected config by year (bets, ROI):", "", per_year.round(4).to_markdown()])


def judge_daily(name, grid, fn, panel, cut):
    rows, keep = [], {}
    for params in grid:
        d, turn = fn(panel, **params)
        is_r, oos_r = d[d.index <= cut], d[d.index > cut]
        mi, mo = metrics(is_r, 365, turn), metrics(oos_r, 365, turn)
        rows.append(dict(params=json.dumps(params), **{f"is_{k}": v for k, v in mi.items()},
                         **{f"oos_{k}": v for k, v in mo.items()}))
        keep[rows[-1]["params"]] = oos_r
    t = pd.DataFrame(rows)
    b = t.loc[t["is_sharpe"].idxmax()]
    o = keep[b["params"]]
    dsr = deflated_sharpe(o, TRIALS, 1 / len(o)) if o.std() > 0 else 0.0
    checks = {"oos_sharpe>=1": b["oos_sharpe"] >= 1, "dsr>=0.95": dsr >= 0.95, "is_sharpe>0": b["is_sharpe"] > 0,
              "max_dd<=25%": b["oos_max_dd"] >= -0.25, "evidence": b["oos_trades"] >= 30}
    verdict = (f"Selected {b['params']}: holdout Sharpe {b['oos_sharpe']:.2f}, CAGR {b['oos_cagr']:+.1%}, "
               f"max DD {b['oos_max_dd']:.1%}, DSR {dsr:.2f} → **{'PASS' if all(checks.values()) else 'FAIL'}** "
               f"({', '.join(k for k, v in checks.items() if not v)})")
    return "\n".join([f"## {name}", "", verdict, "", fmt(t)])


def part_funding():
    p = r7.funding_panel(refresh=True)
    cover = {c: (str(p["hl"][c].first_valid_index())[:10], int(p["hl"][c].notna().sum())) for c in r7.COINS}
    md = judge_daily("7C. Cross-exchange funding arbitrage (Hyperliquid vs Binance)", r7.FUNDING_GRID,
                     r7.funding_arb, p, "2024-12-31")
    gap = (p["hl"] - p["bn"]).abs().mean() * 365
    return md + f"\n\nHyperliquid coverage (first day, days): {cover}\n\nMean |daily funding gap| ×365: " \
                + ", ".join(f"{c} {v:.1%}" for c, v in gap.items())


def part_pairs():
    from edge import data
    return judge_daily("7D. Crypto pairs trading", r7.PAIRS_GRID, r7.pairs, data.crypto_panel(refresh=True),
                       "2022-12-31")


if __name__ == "__main__":
    part = sys.argv[1]
    md = {"arb": part_arb, "tennis": part_tennis, "funding": part_funding, "pairs": part_pairs}[part]()
    (REPORTS / f"round7_{part}.md").write_text(md + "\n")
    print(md)
