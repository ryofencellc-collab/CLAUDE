"""Round 20 runner (PROTOCOL_ROUND20.md). python run_round20.py list | fetch <series> | report
R20_SMALL=1: KXBTC15M and KXWTAMATCH, 7 days."""
import json
import os
import sys
from pathlib import Path

import pandas as pd

from edge import round20

SMALL = os.environ.get("R20_SMALL") == "1"
A, B = pd.Timestamp("2026-07-01", tz="UTC"), pd.Timestamp("2026-09-30", tz="UTC")
if SMALL:
    A = B - pd.Timedelta(days=7)
SERIES = ["KXBTC15M", "KXETH15M", "KXSOL15M", "KXXRP15M", "KXDOGE15M", "KXHYPE15M", "KXNEAR15M", "KXZEC15M",
          "KXBNB15M", "KXGOLD15M", "KXSILVER15M", "KXWTI15M", "KXNATGAS15M", "KXCOPPER15M", "KXPLATINUM15M",
          "KXPALLADIUM15M", "KXEURUSD15M", "KXBTCD", "KXETHD", "KXBTC", "KXSOLD", "KXXRPD", "KXWTAMATCH",
          "KXITFMATCH", "KXITFWMATCH", "KXATPCHALLENGERMATCH", "KXPGAR1LEAD", "KXPGATOUR", "KXUEFANLGAME",
          "KXUEFANLTOTAL", "KXINTLFRIENDLYGAME", "KXEWSLGAME", "KXURYPDGAME", "KXJ2LEAGUEGAME", "KXCANPLGAME",
          "KXNFL1H", "KXNFL1HSPREAD", "KXNFL1HTOTAL", "KXLOLGAME", "KXCS2GAME", "KXCS2MAP", "KXTRUMPMENTION",
          "KXTRUMPAPPROVE", "KXRAIN", "KXTEMPNYCHS", "KXTEMPMIAH", "KXHIGHCHI"]
DATA, REPORTS = Path("data/r20"), Path("reports")


def report():
    fs = [pd.read_pickle(p) for p in DATA.glob("*.pkl")]
    fs = [f for f in fs if len(f)]
    lines = [f"# Round 20{' SMOKE TEST' if SMALL else ''}: blind 98-99c maker bids on Kalshi favorites", "",
             f"Rules: [PROTOCOL_ROUND20.md](../PROTOCOL_ROUND20.md). Window {A.date()} to {(B - pd.Timedelta(days=1)).date()}.", ""]
    if not fs:
        lines += ["No long-shot fills.", "", "## Verdict: **FAIL**"]
    else:
        f = pd.concat(fs, ignore_index=True)
        f["day"] = f["time"].dt.floor("D")
        daily = f.groupby("day")["pnl"].sum()
        total = f["pnl"].sum()
        last30 = daily[daily.index >= B - pd.Timedelta(days=30)].sum()
        checks = {"net profit >= $3,000": total >= 3000, "profitable on >= 80% of days": (daily > 0).mean() >= 0.8,
                  "worst day >= -$300": daily.min() >= -300, "last 30 days >= 20% of total": total > 0 and last30 >= 0.2 * total}
        per = f.groupby("series").agg(fills=("pnl", "size"), contracts=("count", "sum"), longshot_wins=("won_longshot", "sum"),
                                      net_25=("pnl", "sum"), net_100=("pnl_100", "sum"),
                                      median_min_to_close=("min_to_close", "median")).sort_values("net_25", ascending=False)
        bins = pd.cut(f["min_to_close"], [-1e9, 1, 5, 15, 60, 240, 1e9], labels=["<1m", "1-5m", "5-15m", "15-60m", "1-4h", ">4h"])
        tc = f.groupby(bins, observed=False).agg(fills=("pnl", "size"), longshot_wins=("won_longshot", "sum"), net_25=("pnl", "sum"))
        ok = all(checks.values()) and not SMALL
        lines += [f"## Verdict: **{'PASS' if ok else 'FAIL'}**{' (smoke)' if SMALL else ''}", "", "| | |", "|---|---|",
                  f"| Long-shot fills | {len(f):,} ({int(f['won_longshot'].sum())} long shots won) |",
                  f"| Net profit at 25% capture | **${total:,.2f}** (100%: ${f['pnl_100'].sum():,.2f}) |",
                  f"| Days | {len(daily)} (profitable {(daily > 0).mean():.0%}); average ${daily.mean():,.2f}/day |",
                  f"| Worst day | ${daily.min():,.2f} |", f"| Last 30 days | ${last30:,.2f} |", "",
                  "| Check | Result |", "|---|---|"] + [f"| {k} | {'yes' if v else '**no**'} |" for k, v in checks.items()] + \
                 ["", "## Per series", "", per.round(2).to_markdown(), "", "## By minutes to close", "", tc.round(2).to_markdown(),
                  "", "## Worst 15 fills", "", f.nsmallest(15, "pnl")[["series", "ticker", "time", "px", "count", "pnl", "min_to_close"]].round(2).to_markdown(index=False)]
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / ("ROUND20_SMOKE.md" if SMALL else "ROUND20.md")).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "list":
        print(json.dumps(["KXBTC15M", "KXWTAMATCH"] if SMALL else SERIES))
    elif mode == "fetch":
        DATA.mkdir(parents=True, exist_ok=True)
        round20.scan(sys.argv[2], A, B).to_pickle(DATA / f"{sys.argv[2]}.pkl")
    else:
        report()
