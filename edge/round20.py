"""Round 20 (PROTOCOL_ROUND20.md): rest 98-99c bids on the favorite of any Kalshi market, blind.

Every public trade where a taker bought a side at <= 2c was filled by a maker bidding >= 98c on the
other side. We take CAPTURE of each such fill. After settlement the maker earned px per contract
(long shot lost) or lost 1 - px (long shot won), minus the maker fee rounded up per fill. No outcome
knowledge is used, so this is the real risk of always backing the heavy favorite.
"""
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from edge import round15 as r15
from edge import weather as wx

CAPTURE = 0.25
LONGSHOT = 0.02
MAX_PAGES = 400


def markets(series: str, a: pd.Timestamp, b: pd.Timestamp) -> list[dict]:
    """Settled markets of a series closing in [a, b), from the live and historical endpoints."""
    out = {}
    for path in ("markets", "historical/markets"):
        cursor, pages, kept = None, 0, 0
        while pages < MAX_PAGES:
            pages += 1
            p = {"series_ticker": series, "limit": 1000, "min_close_ts": int(a.timestamp()), "max_close_ts": int(b.timestamp())}
            if path == "markets":
                p["status"] = "settled"
            if cursor:
                p["cursor"] = cursor
            r = wx._get(f"{wx.KALSHI}/{path}", p)
            if r is None or r.status_code != 200:
                break
            j = r.json()
            page = j.get("markets", [])
            closes = pd.to_datetime([m.get("close_time") for m in page], utc=True, errors="coerce")
            for m, c in zip(page, closes):
                if m.get("result") in ("yes", "no") and pd.notna(c) and a <= c < b:
                    out.setdefault(m["ticker"], m)
                    kept += 1
            cursor = j.get("cursor")
            if pages % 20 == 1 or not cursor:
                print(f"    {series} {path} page {pages}: closes {closes.min()} .. {closes.max()}, kept {kept}", flush=True)
            if not cursor or not page or (len(closes) and closes.max() < a):  # pages run newest first
                break
    return list(out.values())


def fills(m: dict, tr: pd.DataFrame) -> pd.DataFrame:
    if tr.empty:
        return pd.DataFrame()
    tr = tr.copy()
    tr["px"] = np.where(tr["taker_side"] == "yes", tr["yes_price"], tr["no_price"])
    hit = tr[(tr["px"] > 0) & (tr["px"] <= LONGSHOT + 1e-9)].copy()
    if hit.empty:
        return hit
    close = pd.to_datetime(m.get("close_time"), utc=True, errors="coerce")
    hit["won_longshot"] = hit["taker_side"] == m["result"]
    n = hit["count"] * CAPTURE
    fee = np.array([r15._maker_fee(x, 1 - p) if x > 0 else 0.0 for x, p in zip(n, hit["px"])])
    hit["pnl"] = np.where(hit["won_longshot"], -(1 - hit["px"]) * n, hit["px"] * n) - fee
    hit["pnl_100"] = np.where(hit["won_longshot"], -(1 - hit["px"]) * hit["count"], hit["px"] * hit["count"]) - \
        np.array([r15._maker_fee(x, 1 - p) for x, p in zip(hit["count"], hit["px"])])
    hit["min_to_close"] = (close - hit["time"]).dt.total_seconds() / 60
    hit["ticker"] = m["ticker"]
    return hit[["ticker", "time", "taker_side", "px", "count", "won_longshot", "pnl", "pnl_100", "min_to_close"]]


def scan(series: str, a: pd.Timestamp, b: pd.Timestamp) -> pd.DataFrame:
    t0 = time.time()
    ms = markets(series, a, b)
    print(f"  {series}: {len(ms)} markets listed in {time.time() - t0:.0f}s", flush=True)
    done = [0]

    def one(m):
        tr = r15.trades(m["ticker"])
        done[0] += 1
        if done[0] % 200 == 0:
            print(f"    trades for {done[0]}/{len(ms)} markets, {time.time() - t0:.0f}s", flush=True)
        return tr

    with ThreadPoolExecutor(8) as ex:
        trs = list(ex.map(one, ms))
    parts = [fills(m, t) for m, t in zip(ms, trs)]
    parts = [p for p in parts if len(p)]
    out = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    print(f"  {series}: {len(ms)} markets, {sum(len(t) for t in trs):,} trades, {len(out):,} long-shot fills, "
          f"{int(out['won_longshot'].sum()) if len(out) else 0} long shots won, "
          f"net ${out['pnl'].sum() if len(out) else 0:,.2f}", flush=True)
    if len(out):
        out["series"] = series
    return out
