"""Round 5: Kalshi daily-high temperature markets vs archived weather forecasts.

See PROTOCOL_ROUND5.md (incl. amendments 1-2). Everything a trade uses is
known at 09:00 local on the target day: the quote at that hour and forecasts
from model runs published before ~04:00 local.
"""
import math
import re
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import NormalDist

import numpy as np
import pandas as pd
import requests

from edge.data import CACHE

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
STAKE, DECISION_HOUR, HOLDOUT_DAYS = 10.0, 9, 120
MODELS = ["gfs_seamless", "ecmwf_ifs025", "icon_seamless", "gem_seamless", "jma_seamless"]
PHI = NormalDist().cdf
_s = requests.Session()

# the original 14 US cities ("major") by title keyword: (lat, lon, tz) of the NWS climate site
MAJOR = {
    "new york": (40.779, -73.969, "America/New_York"), "nyc": (40.779, -73.969, "America/New_York"),
    "chicago": (41.786, -87.752, "America/Chicago"), "miami": (25.788, -80.317, "America/New_York"),
    "austin": (30.183, -97.680, "America/Chicago"), "los angeles": (33.938, -118.389, "America/Los_Angeles"),
    "denver": (39.847, -104.656, "America/Denver"), "philadelphia": (39.873, -75.227, "America/New_York"),
    "houston": (29.638, -95.282, "America/Chicago"), "new orleans": (29.993, -90.251, "America/Chicago"),
    "atlanta": (33.630, -84.442, "America/New_York"), "phoenix": (33.428, -112.004, "America/Phoenix"),
    "san francisco": (37.620, -122.365, "America/Los_Angeles"), "washington": (38.848, -77.034, "America/New_York"),
    "dc": (38.848, -77.034, "America/New_York"), "minneapolis": (44.883, -93.229, "America/Chicago"),
}
# everything else ("minor"), by airport code at the end of the series ticker, or title keyword
MINOR = {
    "TTN": (40.277, -74.816, "America/New_York"), "SAN": (32.734, -117.183, "America/Los_Angeles"),
    "OKC": (35.389, -97.601, "America/Chicago"), "MMMX": (19.436, -99.072, "America/Mexico_City"),
    "ZBAA": (40.080, 116.585, "Asia/Shanghai"), "CYYZ": (43.677, -79.631, "America/Toronto"),
    "RJTT": (35.553, 139.781, "Asia/Tokyo"), "LFPG": (49.010, 2.548, "Europe/Paris"),
    "VHHH": (22.308, 113.918, "Asia/Hong_Kong"), "EGLL": (51.470, -0.454, "Europe/London"),
    "VABB": (19.089, 72.868, "Asia/Kolkata"), "WSSS": (1.350, 103.994, "Asia/Singapore"),
    "EDDB": (52.362, 13.501, "Europe/Berlin"), "LAS": (36.072, -115.163, "America/Los_Angeles"),
    "SEA": (47.444, -122.314, "America/Los_Angeles"), "BOS": (42.361, -71.010, "America/New_York"),
    "DFW": (32.898, -97.019, "America/Chicago"), "SAT": (29.544, -98.484, "America/Chicago"),
    "LIRF": (41.800, 12.239, "Europe/Rome"), "LEMD": (40.472, -3.561, "Europe/Madrid"),
    "YSSY": (-33.946, 151.177, "Australia/Sydney"), "RKSI": (37.469, 126.451, "Asia/Seoul"),
    "OMDB": (25.253, 55.364, "Asia/Dubai"), "SBGR": (-23.435, -46.473, "America/Sao_Paulo"),
}
MINOR_WORDS = {"las vegas": "LAS", "seattle": "SEA", "boston": "BOS", "dallas": "DFW",
               "san antonio": "SAT", "oklahoma": "OKC", "san diego": "SAN", "trenton": "TTN"}
MONTHS = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG",
                                      "SEP", "OCT", "NOV", "DEC"], 1)}


def _get(url, params=None, tries=6):
    for i in range(tries):
        try:
            r = _s.get(url, params=params, timeout=60)
        except requests.RequestException:
            time.sleep(2 ** i)
            continue
        if r.status_code == 429:
            time.sleep(2 ** i)
            continue
        return r
    return None


def locate(ticker, title):
    """(name, tier, lat, lon, tz) for a daily-high series, or None."""
    t = title.lower()
    for code, loc in MINOR.items():
        if ticker.endswith(code):
            return (code, "minor", *loc)
    for word, code in MINOR_WORDS.items():
        if word in t:
            return (code, "minor", *MINOR[code])
    for word, loc in MAJOR.items():
        if word in t:
            return ("new york" if word == "nyc" else "washington" if word == "dc" else word, "major", *loc)
    return None


def daily_high_series():
    r = _get(f"{KALSHI}/series", {"category": "Climate and Weather"})
    out = []
    for s in r.json().get("series", []):
        title = s["title"].lower()
        if not any(w in title for w in ("highest temperature", "high temp", "max temp", "maximum high")):
            continue
        if any(w in title for w in ("week", "average", "month", "year", "cities")) or s["ticker"] == "KXMAXTEMP100":
            continue
        loc = locate(s["ticker"], s["title"])
        if loc:
            out.append((s["ticker"], *loc))
        else:
            print(f"  skip series without location: {s['ticker']} | {s['title']}")
    return out


def _target_date(event_ticker):
    m = re.search(r"-(\d{2})([A-Z]{3})(\d{2})$", event_ticker)
    if not m:
        return None
    return pd.Timestamp(2000 + int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)))


def markets(series):
    """Settled markets from the live API plus Kalshi's historical archive (older than its cutoff)."""
    out = {}
    for path, extra in (("markets", {"status": "settled"}), ("historical/markets", {})):
        cursor = None
        while True:
            p = {"series_ticker": series, "limit": 1000, **extra}
            if cursor:
                p["cursor"] = cursor
            r = _get(f"{KALSHI}/{path}", p)
            if r is None or r.status_code != 200:
                break
            j = r.json()
            for m in j.get("markets", []):
                out.setdefault(m["ticker"], {**m, "_archive": path.startswith("historical")})
            cursor = j.get("cursor")
            if not cursor or not j.get("markets"):
                break
    return list(out.values())


def _quote(series, m, tz):
    """yes_bid / yes_ask at 09:00 local on the target day (latest hourly close within 3h)."""
    day = _target_date(m["event_ticker"])
    decide = pd.Timestamp(day.year, day.month, day.day, DECISION_HOUR).tz_localize(tz).tz_convert("UTC")
    t1 = int(decide.timestamp())
    q = {"start_ts": t1 - 3 * 3600, "end_ts": t1, "period_interval": 60}
    urls = [f"{KALSHI}/series/{series}/markets/{m['ticker']}/candlesticks",
            f"{KALSHI}/historical/markets/{m['ticker']}/candlesticks"]
    if m.get("_archive"):
        urls.reverse()
    for url in urls:
        r = _get(url, q)
        if r is not None and r.status_code == 200 and r.json().get("candlesticks"):
            break
    else:
        return None
    best = None
    for c in r.json().get("candlesticks", []):
        if c["end_period_ts"] <= t1:
            ask, bid = c.get("yes_ask", {}).get("close_dollars"), c.get("yes_bid", {}).get("close_dollars")
            if ask is not None and bid is not None:
                best = (float(bid), float(ask))
    return best


def forecasts(lat, lon, tz, start, end, unit):
    """Daily max of the previous-day-run forecast, one column per model that has data."""
    cols = {}
    for model in MODELS:
        r = _get("https://previous-runs-api.open-meteo.com/v1/forecast", dict(
            latitude=lat, longitude=lon, start_date=start, end_date=end, timezone=tz,
            hourly="temperature_2m_previous_day1", models=model, temperature_unit=unit))
        if r is None or r.status_code != 200:
            continue
        h = r.json().get("hourly", {})
        vals = h.get("temperature_2m_previous_day1")
        if not vals:
            continue
        s = pd.Series(vals, index=pd.to_datetime(h["time"]), dtype=float)
        cols[model] = s.groupby(s.index.normalize()).max(min_count=18)
    f = pd.DataFrame(cols)
    out = pd.DataFrame(index=f.index)
    out["gfs"] = f.get("gfs_seamless")
    out["multi"] = f.mean(axis=1).where(f.notna().sum(axis=1) >= 2)
    return out


def _unit(m):
    text = (m.get("rules_primary") or "") + (m.get("yes_sub_title") or "") + (m.get("no_sub_title") or "")
    return "celsius" if ("°C" in text or "celsius" in text.lower()) else "fahrenheit"


def dataset(refresh=False) -> pd.DataFrame:
    path = CACHE / "weather.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    rows = []
    for series, city, tier, lat, lon, tz in daily_high_series():
        ms = [m for m in markets(series) if _target_date(m["event_ticker"]) is not None
              and m.get("result") in ("yes", "no")]
        if not ms:
            continue
        days = sorted({_target_date(m["event_ticker"]) for m in ms})
        unit = _unit(ms[0])
        fc = forecasts(lat, lon, tz, days[0].date().isoformat(), days[-1].date().isoformat(), unit)
        with ThreadPoolExecutor(16) as ex:
            quotes = list(ex.map(lambda m: _quote(series, m, tz), ms))
        for m, q in zip(ms, quotes):
            d = _target_date(m["event_ticker"])
            ev = pd.to_numeric(m.get("expiration_value"), errors="coerce")
            rows.append(dict(series=series, city=city, tier=tier, unit=unit, date=d, ticker=m["ticker"],
                             event=m["event_ticker"], strike_type=m.get("strike_type"),
                             floor=m.get("floor_strike"), cap=m.get("cap_strike"),
                             yes_won=m["result"] == "yes", volume=pd.to_numeric(m.get("volume_fp", m.get("volume")),
                                                                                  errors="coerce"),
                             bid=q[0] if q else np.nan, ask=q[1] if q else np.nan,
                             gfs=fc["gfs"].get(d, np.nan), multi=fc["multi"].get(d, np.nan), observed=ev))
        print(f"  {series} ({city}, {tier}, {unit}): {len(ms)} markets, {len(days)} days "
              f"{days[0].date()}..{days[-1].date()}, quoted {sum(q is not None for q in quotes)}, "
              f"multi-model days {int(fc['multi'].notna().sum())}", flush=True)
    df = pd.DataFrame(rows)
    df.to_pickle(path)
    return df


def prob_yes(row, mu, sd):
    f, c, t = row["floor"], row["cap"], row["strike_type"]
    above = lambda k: 1 - PHI((k + 0.5 - mu) / sd)   # P(high > k), integer highs
    below = lambda k: PHI((k - 0.5 - mu) / sd)       # P(high < k)
    if t == "greater":
        return above(f)
    if t == "less":
        return below(c)
    if t == "between" and f is not None and c is not None:
        return PHI((c + 0.5 - mu) / sd) - PHI((f - 0.5 - mu) / sd)
    return np.nan


def fee(contracts, price):
    return math.ceil(0.07 * contracts * price * (1 - price) * 100 - 1e-9) / 100


def bets(df, calib, edge, per_event, fc="gfs"):
    out = []
    for _, r in df.dropna(subset=[fc, "bid", "ask"]).iterrows():
        if r["city"] not in calib:
            continue
        bias, sd = calib[r["city"]]
        p = prob_yes(r, r[fc] + bias, sd)
        if not np.isfinite(p):
            continue
        for side, prob, price in (("yes", p, r["ask"]), ("no", 1 - p, 1 - r["bid"])):
            if 0.01 <= price <= 0.99 and prob - price >= edge:
                n = STAKE / price
                won = r["yes_won"] if side == "yes" else not r["yes_won"]
                pnl = n * won - STAKE - fee(n, price)
                out.append(dict(date=r["date"], city=r["city"], event=r["event"], side=side,
                                price=price, prob=prob, edge=prob - price, won=won, pnl=pnl))
    b = pd.DataFrame(out)
    if per_event == "best" and len(b):
        b = b.loc[b.groupby("event")["edge"].idxmax()]
    return b.sort_values("date") if len(b) else b


def calibrate(df, fc="gfs"):
    """Per-city bias and sd of (settled value - forecast), one row per city-day."""
    d = df.drop_duplicates(["city", "date"]).dropna(subset=[fc, "observed"])
    err = d["observed"] - d[fc]
    floor = {"celsius": 0.8, "fahrenheit": 1.5}
    units = d.groupby("city")["unit"].first()
    return {c: (float(e.mean()), max(float(e.std()), floor[units[c]]))
            for c, e in err.groupby(d["city"]) if len(e) >= 20}


GRID = [dict(edge=e, per_event=p) for e in (0.05, 0.10, 0.15) for p in ("best", "all")]
