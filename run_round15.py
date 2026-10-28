"""Round 15 runner (PROTOCOL_ROUND15.md): Kalshi weather "first money in".

    python run_round15.py list            # JSON list of US daily-high series
    python run_round15.py fetch <series>  # data/r15/<series>_{dec,opp}.pkl
    python run_round15.py report          # reports/ROUND15.md
R15_SMALL=1: New York only, last 60 days.
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd

from edge import round15, weather as wx

SMALL = os.environ.get("R15_SMALL") == "1"
TAG = os.environ.get("R15_TAG", "15")  # "17" = the 99c sweep (PROTOCOL_ROUND17.md), same pipeline
END = pd.Timestamp("2026-10-26")
START = END - pd.Timedelta(days=60 if SMALL else 364)
DATA = Path(f"data/r{TAG}")
REPORTS = Path("reports")


def us_series():
    out = [s for s in wx.daily_high_series() if s[1] in round15.STATIONS]
    return [s for s in out if s[1] == "new york"] if SMALL else out


def fetch(series):
    spec = next(s for s in us_series() if s[0] == series)
    name, city, tier, lat, lon, tz = spec
    dec, opp = round15.scan_series(name, city, tz, START, END)
    DATA.mkdir(parents=True, exist_ok=True)
    dec.to_pickle(DATA / f"{series}_dec.pkl")
    opp.to_pickle(DATA / f"{series}_opp.pkl")


def report():
    dec = pd.concat([pd.read_pickle(p) for p in DATA.glob("*_dec.pkl")], ignore_index=True)
    opps = [pd.read_pickle(p) for p in DATA.glob("*_opp.pkl")]
    opp = pd.concat([o for o in opps if len(o)], ignore_index=True) if any(len(o) for o in opps) else pd.DataFrame()
    acc = dec["correct"].mean() if len(dec) else float("nan")
    misses = dec[~dec["correct"]]
    title = "Kalshi weather first-money-in" if TAG == "15" else f"sweep decided weather outcomes at <= {round15.MAX_PRICE:.2f}"
    lines = [f"# Round {TAG}{' SMOKE TEST (New York, 60 days)' if SMALL else ''}: {title}", "",
             f"Rules: [PROTOCOL_ROUND{TAG}.md](../PROTOCOL_ROUND{TAG}.md). Window {START.date()} to {END.date()}.", "",
             f"Decided markets: {len(dec):,} (tradable before close: {int(dec['tradable'].sum()) if len(dec) else 0:,}); "
             f"decided calls correct: **{acc:.2%}** ({len(misses)} misses)."]
    if opp.empty:
        lines += ["", "No trade bought a decided outcome at 97c or less after it was knowable.", "", "## Verdict: **FAIL**"]
    else:
        opp["day"] = pd.to_datetime(opp["date"])
        daily = opp.groupby("day")["profit_25"].sum()
        total25, total100 = opp["profit_25"].sum(), opp["profit_100"].sum()
        last3 = daily[daily.index > END - pd.Timedelta(days=91)].sum()
        checks = {
            "decided calls >= 99.5% right": acc >= 0.995,
            "profit at 25% capture >= $2,000": total25 >= 2000,
            "profitable on >= 60% of opportunity days": (daily > 0).mean() >= 0.60,
            "opportunities on >= 100 days": len(daily) >= 100,
            "last 3 months >= 15% of total": total25 > 0 and last3 >= 0.15 * total25,
        }
        if SMALL:
            checks = {k: v for k, v in checks.items() if "decided" in k}
        ok = all(checks.values())
        by_city = opp.groupby("city").agg(trades=("profit_25", "size"), profit_25=("profit_25", "sum"),
                                          median_price=("price", "median"), median_delay_min=("delay_min", "median"))
        lines += ["", f"## Verdict: **{'PASS' if ok else 'FAIL'}**{' (smoke: accuracy check only)' if SMALL else ''}", "",
                  "| | |", "|---|---|",
                  f"| Cheap trades on decided outcomes | {len(opp):,} |",
                  f"| Profit at 25% capture | **${total25:,.2f}** |",
                  f"| Profit if we had taken all of it (100%) | ${total100:,.2f} |",
                  f"| Days with an opportunity | {len(daily)} (profitable {(daily > 0).mean():.0%}) |",
                  f"| Last 3 months, 25% capture | ${last3:,.2f} |",
                  f"| Median minutes from decision to cheap trade | {opp['delay_min'].median():.1f} |",
                  f"| Median price paid | {opp['price'].median():.3f} |",
                  f"| Average profit per day with an opportunity (25%) | ${daily.mean():,.2f} |",
                  f"| Contracts available (100%, capped $100/trade) | {(opp['profit_100'] != 0).sum():,} trades |", "",
                  "| Check | Result |", "|---|---|"] + \
                 [f"| {k} | {'yes' if v else '**no**'} |" for k, v in checks.items()] + \
                 ["", "## By city", "", by_city.round(2).to_markdown()]
    if len(dec) and "n_trades" in dec:
        d = dec[dec["tradable"]]
        lines += ["", "## Diagnostics (decided markets)", "",
                  f"- trades fetched per decided market: median {d['n_trades'].median():.0f}, "
                  f"zero for {(d['n_trades'] == 0).mean():.0%}",
                  f"- trades after the decision was knowable: median {d.get('n_after', pd.Series(dtype=float)).median():.0f}",
                  f"- cheapest decided-side price after the decision: median "
                  f"{d.get('min_price_after', pd.Series(dtype=float)).median():.3f}, "
                  f"share below 0.97: {(d.get('min_price_after', pd.Series(dtype=float)) <= 0.97).mean():.0%}",
                  f"- decided markets per city-day: {len(dec) / max(dec.groupby(['city', 'date']).ngroups, 1):.1f}", "",
                  dec.head(12)[[c for c in ["date", "ticker", "side", "known", "n_trades", "n_after",
                                            "min_price_after", "first_trade", "last_trade"] if c in dec]].to_markdown(index=False)]
    if len(misses):
        lines += ["", "## Decided calls that settled the other way", "",
                  misses[["city", "date", "ticker", "side", "result", "floor", "cap"]].to_markdown(index=False)]
    REPORTS.mkdir(exist_ok=True)
    name = f"ROUND{TAG}_SMOKE.md" if SMALL else f"ROUND{TAG}.md"
    (REPORTS / name).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "list":
        print(json.dumps([s[0] for s in us_series()]))
    elif mode == "fetch":
        fetch(sys.argv[2])
    else:
        report()
