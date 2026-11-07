"""Round 27 runner (PROTOCOL_ROUND27.md).
python run_round27.py scan SHARD NSHARDS   -> data/r27/shard_SHARD.pkl
python run_round27.py report               -> reports/ROUND27.md"""
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round27 as r

DATA, OUT = Path("data/r27"), Path("reports/ROUND27.md")
NOW = pd.Timestamp.now(tz="UTC").floor("h")
WINDOWS = {"dev": (NOW - pd.Timedelta(days=15), NOW - pd.Timedelta(days=8)),
           "hold": (NOW - pd.Timedelta(days=7), NOW - pd.Timedelta(days=1))}
MAX_SERIES, PER_WINDOW, MIN_VOLUME = 700, 40, 20000


def chosen_series() -> list[dict]:
    ss = r.series_list()
    for x in ss:
        try:
            x["_vol"] = float(x.get("volume_fp") or x.get("volume") or 0)
        except (TypeError, ValueError):
            x["_vol"] = 0.0
    ss = [x for x in ss if x["_vol"] >= MIN_VOLUME]
    return sorted(ss, key=lambda x: -x["_vol"])[:MAX_SERIES]


def scan(shard: int, n: int) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    ss = [x for x in chosen_series() if zlib.crc32(x["ticker"].encode()) % n == shard]
    cut = r.cutoff()
    print(f"shard {shard}/{n}: {len(ss)} series; historical cutoff {cut}", flush=True)
    rows = []
    for i, x in enumerate(ss):
        fee = float(x.get("fee_multiplier") or 1)
        for tag, (a, b) in WINDOWS.items():
            ms = sorted(r.settled_markets(x["ticker"], a, b), key=lambda m: m.get("close_time", ""))
            if not ms:
                continue
            w = max(1, -(-len(ms) // PER_WINDOW))
            for m in ms[::w]:
                close = pd.to_datetime(m.get("close_time"), utc=True)
                row = r.market_row(m, r.trades(m["ticker"], close, cut), fee)
                row.update(series=x["ticker"], category=x.get("category", ""), frequency=x.get("frequency", ""),
                           window=tag, weight=w, fee_mult=fee, title=x.get("title", ""))
                rows.append(row)
        if i % 10 == 0:
            print(f"  {i}/{len(ss)} {x['ticker']}: {len(rows)} market rows so far", flush=True)
            pd.DataFrame(rows).to_pickle(DATA / f"shard_{shard}.pkl")
    pd.DataFrame(rows).to_pickle(DATA / f"shard_{shard}.pkl")
    print(f"shard {shard}: done, {len(rows)} rows", flush=True)


def report() -> None:
    parts = [pd.read_pickle(p) for p in sorted(DATA.glob("shard_*.pkl"))]
    d = pd.concat([p for p in parts if len(p)], ignore_index=True)
    agg = []
    for (s, wdw), g in d.groupby(["series", "window"]):
        agg.append({"series": s, "window": wdw, "category": g["category"].iloc[0], "frequency": g["frequency"].iloc[0],
                    "title": g["title"].iloc[0][:40], "structure": g["structure"].mode().iloc[0] if len(g) else "",
                    **r.summarize(g)})
    a = pd.DataFrame(agg)
    dev, hold = a[a["window"] == "dev"].set_index("series"), a[a["window"] == "hold"].set_index("series")
    cand = dev[(dev["pnl"] > 0) & (dev["with_fills"] >= 10) & (dev["win_rate"] < 0.005)].index
    rows = []
    for s in cand:
        h = hold.loc[s] if s in hold.index else None
        ok = h is not None and h["pnl"] > 0 and (h["worst"] >= -h["pnl"])
        rows.append({"series": s, "category": dev.at[s, "category"], "title": dev.at[s, "title"],
                     "structure": dev.at[s, "structure"], "freq": dev.at[s, "frequency"],
                     "dev $ (sampled)": round(dev.at[s, "pnl"], 2), "dev $ x weight": round(dev.at[s, "pnl_x_weight"], 2),
                     "dev fills mkts": int(dev.at[s, "with_fills"]), "dev LS win%": round(100 * dev.at[s, "win_rate"], 3),
                     "hold $ (sampled)": round(h["pnl"], 2) if h is not None else np.nan,
                     "hold $ x weight": round(h["pnl_x_weight"], 2) if h is not None else np.nan,
                     "hold fills mkts": int(h["with_fills"]) if h is not None else 0,
                     "hold losing mkts": int(h["losing_markets"]) if h is not None else 0,
                     "hold worst $": round(h["worst"], 2) if h is not None else np.nan,
                     "lead min": round(dev.at[s, "lead_min"], 1), "CONFIRMED": "yes" if ok else "no"})
    c = pd.DataFrame(rows).sort_values(["CONFIRMED", "hold $ x weight"], ascending=[False, False]) if rows else pd.DataFrame()
    bycat = a.groupby(["window", "category"]).agg(series=("series", "nunique"), pnl=("pnl", "sum"),
                                                  pnl_x_weight=("pnl_x_weight", "sum"),
                                                  losing=("losing_markets", "sum")).round(2)
    lines = ["# Round 27: every Kalshi series, scanned for the 99c maker edge", "",
             "Rules: [PROTOCOL_ROUND27.md](../PROTOCOL_ROUND27.md). Windows: " +
             ", ".join(f"{k} {a_.date()}..{b_.date()}" for k, (a_, b_) in WINDOWS.items()) + ".", "",
             f"Series scanned: {d['series'].nunique()}; markets: {len(d):,}; with long-shot trades at 1-2c: "
             f"{int((d['reach'] > 0).sum()):,}.", "",
             "'$ (sampled)' is what the sampled markets made at 25% capture, 1,000 cap; '$ x weight' scales by the "
             "sampling (an upper bound: one-at-a-time capital and queues are not modelled).", "",
             f"## Candidates (dev) and confirmation (holdout): {len(c)} candidates, "
             f"{int((c['CONFIRMED'] == 'yes').sum()) if len(c) else 0} confirmed", "",
             c.to_markdown(index=False) if len(c) else "none", "", "## By category", "", bycat.to_markdown(), "",
             "## Biggest losers (dev + holdout, by series)", "",
             a.groupby("series")[["pnl", "losing_markets"]].sum().sort_values("pnl").head(15).round(2).to_markdown()]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    a.to_csv(OUT.with_suffix(".csv"), index=False)
    print("\n".join(lines))


if __name__ == "__main__":
    {"scan": lambda: scan(int(sys.argv[2]), int(sys.argv[3])), "report": report}[sys.argv[1]]()
