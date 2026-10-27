"""Forward paper test of the Round 13 portfolio (PROTOCOL_ROUND13.md, "Forward test").

Runs after each US trading day once the crypto daily bar has closed (00:23 UTC).
The procedure is the pre-registered one: the config is re-chosen on 1 January and
1 July from all data before that date; target weights come from closes only.
paper/r13_ledger.csv is append-only: one row per trading day with the weights
held over that day and the resulting paper equity.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round13

ROOT = Path(__file__).resolve().parent.parent / "paper"
ROOT.mkdir(exist_ok=True)
LEDGER = ROOT / "r13_ledger.csv"
START_EQUITY = 10_000.0
FORWARD_START = pd.Timestamp("2026-10-27")  # first close whose target weights are traded


def choose(px: pd.DataFrame, asof: pd.Timestamp) -> str:
    """The pre-registered selection: best net Sharpe from 2007-07-01 up to the latest refit date."""
    refit = pd.Timestamp(asof.year, 1 if asof.month < 7 else 7, 1)
    trend_w = round13.round11.weights(px[round13.ETFS], round13.TREND_CFG)
    sleeves = {n: round13.crypto_sleeve(px, n) for n in (50, 100)}
    train = (px.index >= round13.START) & (px.index < refit)
    best, best_sh = None, -9.0
    for c in round13.configs():
        r = round13.backtest(round13.combine(px, c, trend_w, sleeves), px)[0][train]
        sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else -9.0
        if sh > best_sh:
            best, best_sh = round13.cfg_id(c), sh
    return best


def target(px: pd.DataFrame, cid: str) -> pd.Series:
    core, sma, a, b = cid.split("-")
    c = dict(core=core, sma=int(sma[3:]), alpha=int(a[6:]) / 100, beta=int(b[5:]) / 100)
    trend_w = round13.round11.weights(px[round13.ETFS], round13.TREND_CFG)
    sleeves = {n: round13.crypto_sleeve(px, n) for n in (50, 100)}
    return round13.combine(px, c, trend_w, sleeves).iloc[-1]


def step(px: pd.DataFrame, now: pd.Timestamp | None = None) -> pd.DataFrame:
    """Book every completed trading day since the last ledger row; set the next target."""
    cols = round13.ASSETS
    led = pd.read_csv(LEDGER, parse_dates=["date"]) if LEDGER.exists() else pd.DataFrame()
    rets = px.pct_change(fill_method=None).fillna(0.0)
    days = px.index[px.index >= FORWARD_START]
    if led.empty:
        last_date, equity, held = None, START_EQUITY, pd.Series(0.0, index=cols)
    else:
        last = led.iloc[-1]
        last_date, equity = last["date"], float(last["equity"])
        held = pd.Series({c: float(last[f"w_{c}"]) for c in cols})
    rows = []
    for d in days:
        if last_date is not None and d <= last_date:
            continue
        hist = px.loc[:d]
        cid = choose(hist, d)
        new = target(hist, cid)
        if last_date is not None or rows:
            pnl = float((held * rets.loc[d, cols]).sum())
        else:
            pnl = 0.0  # first day: nothing held yet
        cost = float((new - held).abs().mul(pd.Series(round13.COSTS)[cols]).sum())
        equity = equity * (1 + pnl) * (1 - cost)
        rows.append({"date": d.date().isoformat(), "config": cid, "day_return": round(pnl, 6),
                     "cost": round(cost, 6), "equity": round(equity, 2),
                     **{f"w_{c}": round(float(new[c]), 4) for c in cols}})
        held = new
    if rows:
        out = pd.concat([led, pd.DataFrame(rows)], ignore_index=True) if not led.empty else pd.DataFrame(rows)
        out.to_csv(LEDGER, index=False)
        led = out
    return led


def summary(led: pd.DataFrame) -> str:
    if led.empty:
        return "# Round 13 forward paper test\n\nNo trading days booked yet.\n"
    eq = led["equity"].astype(float)
    r = led["day_return"].astype(float).iloc[1:]
    last = led.iloc[-1]
    w = {c: last[f"w_{c}"] for c in round13.ASSETS if float(last[f"w_{c}"]) > 0}
    lines = ["# Round 13 forward paper test (live, unseen data)", "",
             f"Rules: [PROTOCOL_ROUND13.md](../PROTOCOL_ROUND13.md), \"Forward test\". Started "
             f"{FORWARD_START.date()} with ${START_EQUITY:,.0f} paper.", "",
             "| | |", "|---|---|",
             f"| Trading days booked | {len(led)} |",
             f"| Paper equity | **${eq.iloc[-1]:,.2f}** |",
             f"| Return so far | {eq.iloc[-1] / START_EQUITY - 1:+.2%} |",
             f"| Worst drop so far | {(eq / eq.cummax() - 1).min():.2%} |",
             f"| Green days | {(r > 0).sum()} of {len(r)} |" if len(r) else "| Green days | n/a |",
             f"| Current config | {last['config']} |",
             f"| Current weights | {', '.join(f'{k} {float(v):.0%}' for k, v in w.items()) or 'cash'} |", "",
             "| Date | Day return | Equity |", "|---|---:|---:|"]
    lines += [f"| {x['date']} | {float(x['day_return']):+.2%} | ${float(x['equity']):,.2f} |"
              for _, x in led.tail(30).iterrows()]
    return "\n".join(lines) + "\n"


def run():
    from run_round9b import download
    px = download(round13.ASSETS)[round13.ASSETS].dropna(subset=["SPY"])
    led = step(px)
    (ROOT / "ROUND13_PAPER.md").write_text(summary(led))
    print(summary(led))


if __name__ == "__main__":
    run()
