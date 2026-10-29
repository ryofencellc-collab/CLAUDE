"""Round 21 runner (PROTOCOL_ROUND21.md). python run_round21.py list | fetch <series> | report
R21_SMALL=1: KXBTC15M and KXBTCD, 5 days of each period."""
import json
import os
import sys
from pathlib import Path

import pandas as pd

from edge import round21

SMALL = os.environ.get("R21_SMALL") == "1"
DEV = (pd.Timestamp("2026-04-01", tz="UTC"), pd.Timestamp("2026-09-30", tz="UTC"))
HOLD = (pd.Timestamp("2026-10-01", tz="UTC"), pd.Timestamp("2026-10-28", tz="UTC"))
if SMALL:
    DEV, HOLD = (DEV[1] - pd.Timedelta(days=5), DEV[1]), (HOLD[0], HOLD[0] + pd.Timedelta(days=5))
SERIES = ["KXBTC15M", "KXETH15M", "KXSOL15M", "KXXRP15M", "KXDOGE15M", "KXBNB15M", "KXBTCD", "KXETHD", "KXSOLD", "KXXRPD"]
ZS = [1, 2, 3, 4, 5, 6]
DATA, REPORTS = Path("data/r21"), Path("reports")


def _load(tag):
    fs = [pd.read_pickle(p) for p in DATA.glob(f"*_{tag}.pkl")]
    fs = [f for f in fs if len(f)]
    return pd.concat(fs, ignore_index=True) if fs else pd.DataFrame()


def _stats(f, z):
    b = round21.book(f, z) if len(f) else f
    if b is None or b.empty:
        return dict(z=z, fills=0, net=0.0, days=0, green=0.0, worst=0.0, lw_rate=0.0), b
    daily = b.groupby(b["time"].dt.floor("D"))["pnl"].sum()
    return dict(z=z, fills=len(b), net=b["pnl"].sum(), days=len(daily), green=(daily > 0).mean(), worst=daily.min(),
                lw_rate=b["won_longshot"].mean()), b


def report():
    dev, hold = _load("dev"), _load("hold")
    rows = [_stats(dev, z)[0] for z in ZS]
    grid = pd.DataFrame(rows).set_index("z")
    ok = grid[grid["worst"] >= -150]
    lines = [f"# Round 21{' SMOKE TEST' if SMALL else ''}: maker bids on crypto markets decided by the spot price", "",
             f"Rules: [PROTOCOL_ROUND21.md](../PROTOCOL_ROUND21.md). Dev {DEV[0].date()}..{DEV[1].date()}, "
             f"holdout {HOLD[0].date()}..{HOLD[1].date()}.", "", "## Dev grid (all Z)", "", grid.round(3).to_markdown(), ""]
    if ok.empty or ok["net"].max() <= 0:
        lines += ["No Z qualifies on dev.", "", "## Verdict: **FAIL**"]
    else:
        z = int(ok["net"].idxmax())
        st, b = _stats(hold, z)
        checks = {"holdout net >= $500": st["net"] >= 500, "profitable on >= 80% of days": st["green"] >= 0.8,
                  "worst day >= -$150": st["worst"] >= -150, "long shots win <= 0.5% of fills": st["lw_rate"] <= 0.005}
        verdict = "PASS" if all(checks.values()) and not SMALL else "FAIL"
        lines += [f"Chosen on dev: **Z = {z}**", "", f"## Verdict: **{verdict}**{' (smoke)' if SMALL else ''}", "",
                  "| Holdout | |", "|---|---|", f"| Fills taken | {st['fills']:,} |", f"| Net profit | **${st['net']:,.2f}** |",
                  f"| Days | {st['days']} (green {st['green']:.0%}); per day ${st['net'] / max(st['days'], 1):,.2f} |",
                  f"| Worst day | ${st['worst']:,.2f} |", f"| Long-shot win rate | {st['lw_rate']:.3%} |", "",
                  "| Check | Result |", "|---|---|"] + [f"| {k} | {'yes' if v else '**no**'} |" for k, v in checks.items()]
        hgrid = pd.DataFrame([_stats(hold, zz)[0] for zz in ZS]).set_index("z")
        lines += ["", "## Holdout at every Z (for reference only; the verdict uses the dev choice)", "", hgrid.round(3).to_markdown()]
        if len(b):
            lines += ["", "## Holdout by series", "", b.groupby("series").agg(fills=("pnl", "size"), net=("pnl", "sum"),
                      longshot_wins=("won_longshot", "sum")).round(2).to_markdown(),
                      "", "## Worst holdout fills", "", b.nsmallest(10, "pnl")[["series", "ticker", "time", "px", "n", "z_for_us", "pnl"]].round(3).to_markdown(index=False)]
    have = {p.stem.rsplit("_", 1)[0] for p in DATA.glob("*.pkl")}
    lines += ["", f"Series with no data: {', '.join(s for s in (['KXBTC15M', 'KXBTCD'] if SMALL else SERIES) if s not in have) or 'none'}"]
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / ("ROUND21_SMOKE.md" if SMALL else "ROUND21.md")).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "list":
        print(json.dumps(["KXBTC15M", "KXBTCD"] if SMALL else SERIES))
    elif mode == "fetch":
        DATA.mkdir(parents=True, exist_ok=True)
        for tag, (a, b) in (("dev", DEV), ("hold", HOLD)):
            round21.scan(sys.argv[2], a, b).to_pickle(DATA / f"{sys.argv[2]}_{tag}.pkl")
    else:
        report()
