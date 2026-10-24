"""Prediction markets: Polymarket resolved binary markets and the
favourite-longshot hypothesis from PROTOCOL_ROUND2.md (family C).

No look-ahead: "h hours before close" is measured from the market's
*scheduled* end date, which is known in advance. A market that had already
closed by then is not bettable and is skipped, which is what a live trader
would see too.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

CACHE = Path(__file__).resolve().parent.parent / "data"
CACHE.mkdir(exist_ok=True)
GAMMA = "https://gamma-api.polymarket.com/markets"
CLOB = "https://clob.polymarket.com/prices-history"
SLIPPAGE = 0.01  # pay 1 cent over the quoted price per contract
MIN_VOLUME = 50_000
_s = requests.Session()


def _markets(start="2023-01-01"):
    out, offset = [], 0
    while True:
        r = _s.get(GAMMA, params=dict(closed="true", limit=500, offset=offset,
                                      end_date_min=start, volume_num_min=MIN_VOLUME), timeout=60)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        out.extend(page)
        offset += len(page)
        if offset % 5000 == 0:
            print(f"  markets fetched: {offset}", flush=True)
    return out


def _resolved_binary(m):
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
        prices = [float(p) for p in json.loads(m.get("outcomePrices") or "[]")]
        tokens = json.loads(m.get("clobTokenIds") or "[]")
    except (ValueError, TypeError):
        return None
    if outcomes != ["Yes", "No"] or sorted(prices) != [0.0, 1.0] or len(tokens) != 2:
        return None
    end, closed = pd.to_datetime(m.get("endDate"), utc=True, errors="coerce"), \
        pd.to_datetime(m.get("closedTime"), utc=True, errors="coerce")
    if pd.isna(end) or pd.isna(closed):
        return None
    return dict(id=m["id"], question=m.get("question", ""), yes_token=tokens[0],
                yes_won=prices[0] == 1.0, end=end, closed=closed,
                volume=float(m.get("volumeNum") or 0))


def _history(token, end):
    t1 = int(end.timestamp())
    try:
        r = _s.get(CLOB, params=dict(market=token, startTs=t1 - 3 * 86400, endTs=t1, fidelity=10),
                   timeout=30)
        hist = r.json().get("history", []) if r.status_code == 200 else []
    except (requests.RequestException, ValueError):
        hist = []
    return [(h["t"], float(h["p"])) for h in hist]


def dataset(refresh: bool = False) -> pd.DataFrame:
    """One row per market: YES price at 24h and 1h before scheduled end."""
    path = CACHE / "polymarket.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    ms = [x for x in map(_resolved_binary, _markets()) if x]
    print(f"polymarket: {len(ms)} resolved binary markets with volume >= {MIN_VOLUME}", flush=True)
    with ThreadPoolExecutor(8) as ex:
        hists = list(ex.map(lambda m: _history(m["yes_token"], m["end"]), ms))
    rows = []
    for m, h in zip(ms, hists):
        row = dict(m)
        for hours in (24, 1):
            t = m["end"] - pd.Timedelta(hours=hours)
            pts = [p for ts, p in h if ts <= t.timestamp() and ts >= t.timestamp() - 6 * 3600]
            row[f"p{hours}h"] = pts[-1] if pts and m["closed"] > t else np.nan
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_pickle(path)
    return df


def favourite(df, p_min, hours):
    """Buy whichever side is priced >= p_min, `hours` before scheduled end."""
    yes = df[f"p{hours}h"]
    d = df.dropna(subset=[f"p{hours}h"])
    yes = d[f"p{hours}h"]
    buy_yes = yes >= p_min
    buy_no = (1 - yes) >= p_min
    price = np.where(buy_yes, yes, 1 - yes) + SLIPPAGE
    won = np.where(buy_yes, d["yes_won"], ~d["yes_won"])
    m = (buy_yes | buy_no) & (price < 1)
    return pd.DataFrame({"end": d["end"][m], "ret": (won[m] / price[m]) - 1, "price": price[m]})


FAMILIES = {"pm_favourite": (favourite, [dict(p_min=p, hours=h)
                                         for p in (0.80, 0.90, 0.95) for h in (24, 1)])}
