"""Round 33 (PROTOCOL_ROUND33.md): price-honesty map of Kalshi from real hourly quotes."""
import math
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round20, round31
from edge import weather as wx

OUT = Path("reports/ROUND33.md")
A, B, SPLIT = pd.Timestamp("2026-09-10", tz="UTC"), pd.Timestamp("2026-11-07", tz="UTC"), pd.Timestamp("2026-10-15", tz="UTC")
HORIZONS = (48, 24, 12, 6, 3, 1)
BANDS = [(0.02, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 0.40), (0.40, 0.60), (0.60, 0.80), (0.80, 0.90), (0.90, 0.95), (0.95, 0.99)]
PER_SERIES = 150


def candles(ms: list[dict]) -> pd.DataFrame:
    out = []
    for i in range(0, len(ms), 100):
        chunk = ms[i:i + 100]
        closes = pd.to_datetime([m["close_time"] for m in chunk], utc=True)
        r = wx._get(f"{wx.KALSHI}/markets/candlesticks", {"market_tickers": ",".join(m["ticker"] for m in chunk),
                                                           "start_ts": int((closes.min() - pd.Timedelta(hours=49)).timestamp()),
                                                           "end_ts": int(closes.max().timestamp()), "period_interval": 60})
        if r is None or r.status_code != 200:
            continue
        for mk in r.json().get("markets", []):
            out.append(round31.parse_candles(mk.get("market_ticker"), mk.get("candlesticks")))
    return pd.concat([x for x in out if len(x)], ignore_index=True) if out else pd.DataFrame()


def fetch() -> pd.DataFrame:
    sc = pd.read_csv("reports/ROUND27.csv")[["series", "category"]].drop_duplicates("series")
    sc = sc[~sc["series"].str.endswith("15M")]
    rows = []
    for j, (s, cat) in enumerate(sc.itertuples(index=False)):
        ms = sorted([m for m in round20.markets(s, A, B) if m.get("close_time")], key=lambda m: m["close_time"])
        if not ms:
            continue
        ms = ms[::max(1, -(-len(ms) // PER_SERIES))]
        q = candles(ms)
        if q.empty:
            continue
        meta = pd.DataFrame([{"ticker": m["ticker"], "close": pd.Timestamp(m["close_time"]), "up": float(m["result"] == "yes")} for m in ms])
        q = q.merge(meta, on="ticker")
        for h in HORIZONS:
            at = q[q["t"] <= q["close"] - pd.Timedelta(hours=h)].sort_values("t").groupby("ticker").tail(1)
            at = at[at["t"] > at["close"] - pd.Timedelta(hours=h + 1)]          # the quote must be from that hour
            for x in at.itertuples(index=False):
                rows.append({"series": s, "category": cat, "ticker": x.ticker, "close": x.close, "h": h,
                             "bid": x.bid, "ask": x.ask, "up": x.up})
        if j % 25 == 0:
            print(f"{j}/{len(sc)} {s}: {len(rows):,} quote rows", flush=True)
    return pd.DataFrame(rows)


def taker_fee(p):
    return np.ceil(0.07 * p * (1 - p) * 100 - 1e-9) / 100


def maker_fee(p):
    return np.ceil(0.0175 * p * (1 - p) * 100 - 1e-9) / 100


def bets(d: pd.DataFrame) -> pd.DataFrame:
    d = d[(d["ask"] > d["bid"]) & d["ask"].between(0.01, 0.99) & d["bid"].between(0.01, 0.99)]
    yes = d.assign(side="yes", px=d["ask"], px_maker=d["bid"], won=d["up"] == 1)
    no = d.assign(side="no", px=1 - d["bid"], px_maker=1 - d["ask"], won=d["up"] == 0)
    b = pd.concat([yes, no], ignore_index=True)
    b["band"] = pd.cut(b["px"], [lo for lo, _ in BANDS] + [BANDS[-1][1]], right=False,
                       labels=[f"{int(lo*100)}-{int(hi*100)}c" for lo, hi in BANDS])
    b = b.dropna(subset=["band"])
    b["pnl"] = b["won"].astype(float) - b["px"] - taker_fee(b["px"].to_numpy())
    b["pnl_maker"] = b["won"].astype(float) - b["px_maker"] - maker_fee(b["px_maker"].to_numpy())
    return b


def main():
    d = fetch()
    d.to_pickle("data_r33.pkl")
    b = bets(d)
    rows = []
    for (cat, h, band), g in b.groupby(["category", "h", "band"], observed=True):
        dv, ho = g[g["close"] < SPLIT], g[g["close"] >= SPLIT]
        t = ho["pnl"].mean() / (ho["pnl"].std() / math.sqrt(len(ho))) if len(ho) > 2 and ho["pnl"].std() > 0 else 0.0
        rows.append({"category": cat, "hours left": h, "price band": band, "dev n": len(dv), "dev ¢/bet": round(100 * dv["pnl"].mean(), 2) if len(dv) else np.nan,
                     "hold n": len(ho), "hold ¢/bet": round(100 * ho["pnl"].mean(), 2) if len(ho) else np.nan,
                     "hold win %": round(100 * ho["won"].mean(), 1) if len(ho) else np.nan,
                     "hold avg price": round(100 * ho["px"].mean(), 1) if len(ho) else np.nan,
                     "t": round(t, 2), "maker ¢/bet (upper bound)": round(100 * ho["pnl_maker"].mean(), 2) if len(ho) else np.nan,
                     "EDGE": "YES" if (len(dv) and dv["pnl"].sum() > 0 and ho["pnl"].sum() > 0 and len(ho) >= 100 and t >= 3.5) else ""})
    tab = pd.DataFrame(rows)
    edges = tab[tab["EDGE"] == "YES"].sort_values("t", ascending=False)
    best = tab[(tab["hold n"] >= 100)].sort_values("hold ¢/bet", ascending=False).head(25)
    worst = tab[(tab["hold n"] >= 100)].sort_values("hold ¢/bet").head(15)
    cal = b[b["close"] >= SPLIT].groupby(["category", "band"], observed=True).agg(n=("won", "size"), price=("px", "mean"), won=("won", "mean"))
    cal["gap (won − price), pts"] = (100 * (cal["won"] - cal["price"])).round(1)
    lines = ["# Round 33: price-honesty map of Kalshi (real hourly quotes)", "",
             "Rules: [PROTOCOL_ROUND33.md](../PROTOCOL_ROUND33.md). Taker at the ask with Kalshi's fee, $1 contracts.", "",
             f"Series: {d['series'].nunique()}; markets: {d['ticker'].nunique():,}; quote rows: {len(d):,}. "
             f"Dev closes < {SPLIT.date()} ≤ holdout.", "",
             f"## Edges that pass: {len(edges)}", "", edges.to_markdown(index=False) if len(edges) else "none", "",
             "## Best 25 cells on holdout (≥ 100 bets), pass or not", "", best.to_markdown(index=False), "",
             "## Worst 15 cells (what to avoid)", "", worst.to_markdown(index=False), "",
             "## Calibration by category and price band (holdout, all horizons)", "", cal.round(3).to_markdown()]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
