"""Round 15: Kalshi weather "first money in" (PROTOCOL_ROUND15.md).

Once the station's running high has passed a bracket, the bracket is decided.
This finds every trade that still bought the decided side at <= 97c after the
decision was knowable (reading time + 10 minutes) and books it at 25% capture.
"""
import io
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from edge import weather as wx

STATIONS = {"new york": "NYC", "chicago": "MDW", "miami": "MIA", "austin": "AUS", "los angeles": "LAX",
            "denver": "DEN", "philadelphia": "PHL", "houston": "HOU", "new orleans": "MSY", "atlanta": "ATL",
            "phoenix": "PHX", "san francisco": "SFO", "washington": "DCA", "minneapolis": "MSP",
            "LAS": "LAS", "SEA": "SEA", "BOS": "BOS", "DFW": "DFW", "SAT": "SAT", "OKC": "OKC",
            "SAN": "SAN", "TTN": "TTN"}
IEM = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
DELAY = pd.Timedelta(minutes=10)
MAX_PRICE = float(__import__("os").environ.get("R15_MAX_PRICE", "0.97"))
CAPTURE = 0.25
MAX_STAKE = 100.0


def observations(station: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    """ASOS temperature reports (routine, special, 5-minute), UTC-indexed, deg F."""
    p = dict(station=station, data="tmpf", year1=start.year, month1=start.month, day1=start.day,
             year2=end.year, month2=end.month, day2=end.day, tz="Etc/UTC", format="onlycomma",
             latlon="no", missing="M", trace="T", report_type=[1, 3, 4])
    r = wx._get(IEM, p)
    if r is None or r.status_code != 200:
        return pd.Series(dtype=float)
    df = pd.read_csv(io.StringIO(r.text))
    s = pd.Series(pd.to_numeric(df["tmpf"], errors="coerce").to_numpy(),
                  index=pd.to_datetime(df["valid"]).dt.tz_localize("UTC")).dropna().sort_index()
    return s[~s.index.duplicated()]


def climate_day(date: pd.Timestamp, tz: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Midnight to midnight local *standard* time (the NWS climate day), in UTC."""
    std = datetime(date.year, 1, 15, tzinfo=ZoneInfo(tz)).utcoffset()
    start = pd.Timestamp(date.year, date.month, date.day, tz="UTC") - std
    return start, start + pd.Timedelta(days=1)


def decided(m: dict, obs_day: pd.Series) -> tuple[str, pd.Timestamp] | None:
    """(decided side, first time it was knowable) or None if never decided during the day."""
    f = pd.to_numeric(m.get("floor_strike"), errors="coerce")
    c = pd.to_numeric(m.get("cap_strike"), errors="coerce")
    t = m.get("strike_type")
    if t == "greater" and pd.notna(f):
        side, level = "yes", f + 2
    elif t == "less" and pd.notna(c):
        side, level = "no", c + 1
    elif t == "between" and pd.notna(c):
        side, level = "no", c + 2
    else:
        return None
    hit = obs_day[obs_day.cummax() >= level]
    if hit.empty:
        return None
    return side, hit.index[0] + DELAY


def trades(ticker: str) -> pd.DataFrame:
    rows, seen = [], set()
    for path in ("markets/trades", "historical/trades"):
        cursor = None
        while True:
            p = {"ticker": ticker, "limit": 1000}
            if cursor:
                p["cursor"] = cursor
            r = wx._get(f"{wx.KALSHI}/{path}", p)
            if r is None or r.status_code != 200:
                break
            j = r.json()
            for x in j.get("trades", []):
                if x["trade_id"] not in seen and x.get("ticker") == ticker:
                    seen.add(x["trade_id"])
                    rows.append(x)
            cursor = j.get("cursor")
            if not cursor or not j.get("trades"):
                break
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["created_time"], utc=True, format="ISO8601")
    df["count"] = pd.to_numeric(df.get("count_fp", df.get("count")), errors="coerce")
    df["yes_price"] = pd.to_numeric(df["yes_price_dollars"], errors="coerce")
    df["no_price"] = pd.to_numeric(df["no_price_dollars"], errors="coerce")
    return df


MODE = __import__("os").environ.get("R15_MODE", "taker")  # "maker" = Round 18: resting bids filled by losing-side buyers


def _maker_fee(n, p):
    import math
    return math.ceil(0.0175 * n * p * (1 - p) * 100 - 1e-9) / 100


def opportunities(m: dict, side: str, known: pd.Timestamp, tr: pd.DataFrame, correct: bool) -> list[dict]:
    if tr.empty:
        return []
    price_col = f"{side}_price"
    taker = side if MODE == "taker" else ("no" if side == "yes" else "yes")
    hit = tr[(tr["time"] > known) & (tr["taker_side"] == taker) & (tr[price_col] <= MAX_PRICE)]
    out = []
    for _, x in hit.iterrows():
        p = float(x[price_col])
        n_all = min(float(x["count"]), MAX_STAKE / max(p, 0.01))
        row = dict(ticker=m["ticker"], side=side, correct=correct, known=known, time=x["time"],
                   delay_min=(x["time"] - known).total_seconds() / 60, price=p, count=float(x["count"]))
        for tag, share in (("25", CAPTURE), ("100", 1.0)):
            n = n_all * share
            pay = n * (1.0 if correct else 0.0)
            fee = wx.fee(n, p) if MODE == "taker" else _maker_fee(n, p)
            row[f"profit_{tag}"] = pay - n * p - fee if n > 0 else 0.0
        out.append(row)
    return out


def scan_series(series: str, city: str, tz: str, start: pd.Timestamp, end: pd.Timestamp):
    """Returns (decided-market rows, opportunity rows) for one daily-high series."""
    station = STATIONS.get(city)
    if station is None:
        return pd.DataFrame(), pd.DataFrame()
    ms = [m for m in wx.markets(series) if m.get("result") in ("yes", "no")]
    ms = [m for m in ms if (d := wx._target_date(m["event_ticker"])) is not None and start <= d <= end]
    if not ms:
        return pd.DataFrame(), pd.DataFrame()
    obs = observations(station, start - pd.Timedelta(days=1), end + pd.Timedelta(days=2))
    todo, dec_rows = [], []
    for m in ms:
        d = wx._target_date(m["event_ticker"])
        a, b = climate_day(d, tz)
        dec = decided(m, obs[(obs.index >= a) & (obs.index < b)])
        if dec is None:
            continue
        side, known = dec
        close = pd.to_datetime(m.get("close_time"), utc=True, errors="coerce")
        tradable = known < min(b, close) if pd.notna(close) else known < b
        correct = m["result"] == side
        dec_rows.append(dict(series=series, city=city, date=d, ticker=m["ticker"], side=side, known=known,
                             correct=correct, tradable=tradable, strike_type=m.get("strike_type"),
                             floor=m.get("floor_strike"), cap=m.get("cap_strike"), result=m["result"]))
        if tradable:
            todo.append((m, side, known, correct))
    with ThreadPoolExecutor(4) as ex:
        trs = list(ex.map(lambda x: trades(x[0]["ticker"]), todo))
    opp = []
    diag = {r["ticker"]: r for r in dec_rows}
    for (m, side, known, correct), tr in zip(todo, trs):
        row = diag[m["ticker"]]
        row["n_trades"] = len(tr)
        if len(tr):
            after = tr[tr["time"] > known]
            row["n_after"] = len(after)
            row["min_price_after"] = float(after[f"{side}_price"].min()) if len(after) else np.nan
            row["first_trade"], row["last_trade"] = tr["time"].min(), tr["time"].max()
        for o in opportunities(m, side, known, tr, correct):
            opp.append(dict(series=series, city=city, date=wx._target_date(m["event_ticker"]), **o))
    days = {wx._target_date(m["event_ticker"]) for m in ms}
    print(f"  obs reports {len(obs):,} ({obs.index.min()} .. {obs.index.max()}); market-days {len(days)}; "
          f"trades fetched {sum(len(t) for t in trs):,}", flush=True)
    print(f"  {series} ({city}/{station}): {len(ms)} markets, {len(dec_rows)} decided, {len(todo)} tradable, "
          f"{len(opp)} cheap trades after the decision", flush=True)
    return pd.DataFrame(dec_rows), pd.DataFrame(opp)
