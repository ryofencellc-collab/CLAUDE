"""Fill realism check (reports/FILLCHECK.md).

Kalshi now quotes 0.1c steps between 90c and $1 (price_level_structure 'tapered_deci_cent'). Our bid sits at
99c. A long-shot buyer who pays under 1c for the other side (e.g. 0.5c) trades with a bid ABOVE ours (99.5c),
not with us. The paper fill count treated every long-shot buy at <= 2c as flow that reached our level; any of
it that went to higher bids placed after ours was credited to us by mistake.

For every past paper fill this recounts, from Kalshi's public trade records, only the trades whose other-side
price is >= 1c (the only ones that can reach a 99c bid) and compares the resulting fills and P&L:

  old: filled = min(size, trades at other price <= 2c                  - queue at >= 99c when we bid)
  new: filled = min(size, trades at other price in [1c, 2c]           - queue at >= 99c when we bid)

'new' keeps the whole queue (including bids above 99c, which that flow never reaches): conservative."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from edge import paper21 as P
from edge import weather as wx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "FILLCHECK.md"


def flow(ticker: str, side: str, since: pd.Timestamp, until: pd.Timestamp) -> tuple[float, float]:
    """(long-shot contracts at other price <= 2c, of which at >= 1c) between since and until. Reads both the
    live and the historical trade endpoints (trades older than Kalshi's cutoff move to /historical/trades) and
    counts each trade once."""
    other = "no" if side == "yes" else "yes"
    seen, allc, reach, ok = set(), 0.0, 0.0, False
    for path in ("markets/trades", "historical/trades"):
        cursor = None
        for _ in range(30):
            p = {"ticker": ticker, "limit": 1000, "min_ts": int(since.timestamp()), "max_ts": int(until.timestamp()) + 1}
            if cursor:
                p["cursor"] = cursor
            r = wx._get(f"{wx.KALSHI}/{path}", p)
            if r is None or r.status_code != 200:
                break
            ok = True
            j = r.json()
            for t in j.get("trades", []):
                tid = t.get("trade_id") or (t.get("created_time"), t.get("count_fp"), t.get("yes_price_dollars"))
                if tid in seen:
                    continue
                seen.add(tid)
                ts = pd.Timestamp(t["created_time"])
                px = float(t.get(f"{other}_price_dollars") or 1)
                if t.get("taker_side") == other and px <= 0.02 + 1e-9 and since < ts <= until:
                    n = float(t.get("count_fp") or t.get("count") or 0)
                    allc += n
                    if px >= 0.01 - 1e-9:
                        reach += n
            cursor = j.get("cursor")
            if not cursor or not j.get("trades"):
                break
    return (allc, reach) if ok else (np.nan, np.nan)


def main(limit: int | None = None) -> None:
    f = P._read(P.FILLS, P.COLS)
    f = f[f["series"].isin(P.R22_SERIES)].copy()
    f = f[pd.to_numeric(f["filled"], errors="coerce").fillna(0) > 0]
    if limit:
        f = f.tail(limit)
    rows = []
    for _, x in f.iterrows():
        placed = pd.Timestamp(x["placed_utc"])
        until = pd.Timestamp(x["cancelled_utc"]) if isinstance(x["cancelled_utc"], str) and x["cancelled_utc"] else pd.Timestamp(x["close_utc"])
        allc, reach = flow(x["ticker"], x["side"], placed, until)
        q = float(pd.to_numeric(x["queue_ahead"], errors="coerce") or 0)
        rows.append(dict(ticker=x["ticker"], series=x["series"], status=x["status"], queue=q, seen_logged=float(x["seen"]),
                         flow_all=allc, flow_reach=reach))
    d = pd.DataFrame(rows)
    d = d[np.isfinite(d["flow_all"])]
    for size in (1000.0, 10000.0):
        tag = f"{int(size/1000)}k"
        for kind, col in (("old", "flow_all"), ("new", "flow_reach")):
            n = (d[col] - d["queue"]).clip(lower=0).clip(upper=np.where(d["series"].str.endswith("15M") | (size == 1000), size, 1000))
            d[f"{kind}_{tag}"] = n
            right = (d["status"] == "won").astype(float)
            d[f"pnl_{kind}_{tag}"] = n * (right - 0.99) - [P.r15._maker_fee(v, 0.99) if v > 0 else 0 for v in n]
    lines = ["# Fill realism check (0.1c price steps above 90c)", "", __doc__.split("\n\n", 1)[1].strip(), "",
             f"Markets recounted: {len(d)} (paper fills on Round 21/22 crypto markets). Generated "
             f"{pd.Timestamp.now(tz='UTC'):%Y-%m-%d %H:%M} UTC.", "",
             "| | old count | new count | change |", "|---|---:|---:|---:|"]
    tot_all, tot_reach = d["flow_all"].sum(), d["flow_reach"].sum()
    lines.append(f"| long-shot contracts seen | {tot_all:,.0f} | {tot_reach:,.0f} | {tot_reach / tot_all - 1:+.1%} |" if tot_all else "| long-shot contracts seen | 0 | 0 | |")
    for tag in ("1k", "10k"):
        o, n = d[f"pnl_old_{tag}"].sum(), d[f"pnl_new_{tag}"].sum()
        lines.append(f"| paper P&L at {tag} per market | ${o:,.2f} | ${n:,.2f} | {n / o - 1:+.1%} |" if o else f"| P&L {tag} | 0 | 0 | |")
        fo, fn = (d[f"old_{tag}"] > 0).sum(), (d[f"new_{tag}"] > 0).sum()
        lines.append(f"| markets filled at {tag} | {fo} | {fn} | {fn - fo:+d} |")
    by = d.groupby("series")[["pnl_old_1k", "pnl_new_1k", "pnl_old_10k", "pnl_new_10k"]].sum().round(2)
    lines += ["", "By series:", "", by.to_markdown()]
    lost = d[d["status"] != "won"]
    lines += ["", f"Losing markets in the recount: {len(lost)}; filled under new count: {(lost['new_1k'] > 0).sum()}."]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    d.to_csv(OUT.with_suffix(".csv"), index=False)
    print("\n".join(lines))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
