"""Round 19 runner (PROTOCOL_ROUND19.md). Same modes as run_round15.py.

    python run_round19.py list | fetch <series> | report
R19_SMALL=1: four series, last 60 days, accuracy only.
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd

from edge import round15, round19

SMALL = os.environ.get("R19_SMALL") == "1"
END = pd.Timestamp("2026-10-27")
START = END - pd.Timedelta(days=60 if SMALL else 364)
SPLIT = pd.Timestamp("2026-04-27")
DATA, REPORTS = Path("data/r19"), Path("reports")
SMOKE = {"KXLOWTNYC", "KXHIGHTEGLL", "KXLOWTRJTT", "KXHIGHTEWR"}


def series():
    u = round19.universe()
    return [s for s in u if s[0] in SMOKE] if SMALL else u


def fetch(name):
    spec = next(s for s in series() if s[0] == name)
    _, code, station, tz, kind = spec
    dec, opp = round15.scan_series(name, code, tz, START, END, station=station, kind=kind)
    DATA.mkdir(parents=True, exist_ok=True)
    dec.to_pickle(DATA / f"{name}_dec.pkl")
    opp.to_pickle(DATA / f"{name}_opp.pkl")


def _load(kind):
    fs = [pd.read_pickle(p) for p in DATA.glob(f"*_{kind}.pkl")]
    fs = [f for f in fs if len(f)]
    return pd.concat(fs, ignore_index=True) if fs else pd.DataFrame()


def report():
    dec, opp = _load("dec"), _load("opp")
    lines = [f"# Round 19{' SMOKE TEST' if SMALL else ''}: Round 18 trade on other daily-temperature series", "",
             f"Rules: [PROTOCOL_ROUND19.md](../PROTOCOL_ROUND19.md). Window {START.date()} to {END.date()}.", ""]
    if dec.empty:
        lines += ["No decided markets.", "", "## Verdict: **FAIL**"]
        return _write(lines)
    dec["date"] = pd.to_datetime(dec["date"])
    per = dec.groupby("series").agg(kind=("kind", "first"), decided=("correct", "size"), right=("correct", "mean"))
    if SMALL:
        lines += [f"Decided calls right: **{dec['correct'].mean():.2%}** of {len(dec)}", "", per.to_markdown()]
        miss = dec[~dec["correct"]]
        if len(miss):
            lines += ["", miss[["series", "date", "ticker", "side", "result", "floor", "cap"]].to_markdown(index=False)]
        return _write(lines)
    dev = dec[dec["date"] <= SPLIT].groupby("series")["correct"].agg(["size", "mean"])
    eligible = set(dev[(dev["size"] >= 10) & (dev["mean"] == 1.0)].index)
    per["dev_decided"] = dev["size"]
    per["dev_right"] = dev["mean"]
    per["eligible"] = per.index.isin(eligible)
    hd = dec[(dec["date"] > SPLIT) & dec["series"].isin(eligible)]
    ho = opp[(pd.to_datetime(opp["date"]) > SPLIT) & opp["series"].isin(eligible)] if len(opp) else opp
    acc = hd["correct"].mean() if len(hd) else float("nan")
    if len(ho):
        daily = ho.groupby(pd.to_datetime(ho["date"]))["profit_25"].sum()
        total = ho["profit_25"].sum()
        last3 = daily[daily.index > END - pd.Timedelta(days=91)].sum()
        per["holdout_profit_25"] = ho.groupby("series")["profit_25"].sum()
    else:
        daily, total, last3 = pd.Series(dtype=float), 0.0, 0.0
    checks = {"holdout decided calls >= 99.5% right": acc >= 0.995,
              "holdout profit at 25% capture >= $1,000": total >= 1000,
              "profitable on >= 60% of opportunity days": len(daily) > 0 and (daily > 0).mean() >= 0.60,
              "opportunities on >= 50 days": len(daily) >= 50,
              "last 3 months >= 30% of holdout total": total > 0 and last3 >= 0.30 * total}
    ok = all(checks.values())
    lines += [f"## Verdict: **{'PASS' if ok else 'FAIL'}**", "", "| | |", "|---|---|",
              f"| Series scanned | {len(per)} (eligible after dev screen: {len(eligible)}) |",
              f"| Holdout decided markets | {len(hd):,}, right {acc:.2%} |",
              f"| Holdout profit at 25% capture | **${total:,.2f}** (100%: ${ho['profit_100'].sum() if len(ho) else 0:,.2f}) |",
              f"| Holdout days with an opportunity | {len(daily)} (profitable {(daily > 0).mean() if len(daily) else 0:.0%}) |",
              f"| Average per opportunity day (25%) | ${daily.mean() if len(daily) else 0:,.2f} |",
              f"| Last 3 months (25%) | ${last3:,.2f} |", "",
              "| Check | Result |", "|---|---|"] + [f"| {k} | {'yes' if v else '**no**'} |" for k, v in checks.items()]
    lines += ["", "## Per series", "", per.sort_values("holdout_profit_25" if "holdout_profit_25" in per else "decided",
                                                           ascending=False).round(3).to_markdown()]
    miss = dec[~dec["correct"]]
    if len(miss):
        lines += ["", f"## Decided calls that settled the other way ({len(miss)})", "",
                  miss.head(60)[["series", "date", "ticker", "side", "result", "floor", "cap"]].to_markdown(index=False)]
    _write(lines)


def _write(lines):
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / ("ROUND19_SMOKE.md" if SMALL else "ROUND19.md")).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "list":
        print(json.dumps([s[0] for s in series()]))
    elif mode == "fetch":
        fetch(sys.argv[2])
    else:
        report()
