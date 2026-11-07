"""Crypto spot from three exchanges for the live trader.

Kalshi's 15-minute crypto markets settle on CF Benchmarks' Real Time Index (60-second average before the
close), which is built from several exchanges' trades, including Coinbase, Kraken and Bitstamp. One exchange can
glitch or lag, so the live trader asks all three and acts only when the data agree:

- at least MIN_SOURCES exchanges have complete 1-minute candles no older than STALE and at least MIN_BARS long;
- every fresh close is within DIVERGE of their median (otherwise: no price, so no bid and any bid is pulled);
- the caller scores each fresh close and takes the smallest lead; volatility is the largest of the sources'.

Responses are cached for CACHE_SECONDS: completed 1-minute candles change once a minute, and this keeps each
exchange at well under one request per second."""
import time

import numpy as np
import pandas as pd
import requests

STALE = pd.Timedelta(minutes=3)
MIN_BARS = 30
MIN_SOURCES = 2
DIVERGE = 0.003           # 30 bp from the median: the exchanges normally agree within ~1-10 bp
CACHE_SECONDS = 10
TIMEOUT = 15

# Coinbase product -> each exchange's pair
KRAKEN = {"BTC-USD": "XBTUSD", "ETH-USD": "ETHUSD", "SOL-USD": "SOLUSD", "XRP-USD": "XRPUSD", "DOGE-USD": "XDGUSD"}
BITSTAMP = {"BTC-USD": "btcusd", "ETH-USD": "ethusd", "SOL-USD": "solusd", "XRP-USD": "xrpusd", "DOGE-USD": "dogeusd"}

_s = requests.Session()
_s.headers["User-Agent"] = "live21"
_cache: dict = {}


def _get_json(url: str, params: dict | None = None):
    try:
        r = _s.get(url, params=params, timeout=TIMEOUT)
        return r.json() if r.status_code == 200 else None
    except (requests.RequestException, ValueError):
        return None


def parse_coinbase(j) -> pd.Series:
    """[[start, low, high, open, close, volume], ...] -> closes indexed by candle END time."""
    rows = [x for x in (j or []) if isinstance(x, list) and len(x) >= 5]
    return pd.Series({pd.Timestamp(int(x[0]) + 60, unit="s", tz="UTC"): float(x[4]) for x in rows}, dtype=float)


def parse_kraken(j) -> pd.Series:
    """{"error": [], "result": {"<pair>": [[start, o, h, l, c, vwap, vol, n], ...], "last": n}}."""
    if not isinstance(j, dict) or j.get("error"):
        return pd.Series(dtype=float)
    rows = next((v for k, v in (j.get("result") or {}).items() if k != "last" and isinstance(v, list)), [])
    return pd.Series({pd.Timestamp(int(x[0]) + 60, unit="s", tz="UTC"): float(x[4]) for x in rows if len(x) >= 5},
                     dtype=float)


def parse_bitstamp(j) -> pd.Series:
    """{"data": {"pair": ..., "ohlc": [{"timestamp", "open", "high", "low", "close", "volume"}, ...]}}."""
    rows = ((j or {}).get("data") or {}).get("ohlc") or [] if isinstance(j, dict) else []
    return pd.Series({pd.Timestamp(int(x["timestamp"]) + 60, unit="s", tz="UTC"): float(x["close"])
                      for x in rows if "timestamp" in x and "close" in x}, dtype=float)


def fetch_live(source: str, product: str) -> pd.Series:
    """Raw closes from one exchange (cached); empty on any failure."""
    key = (source, product)
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < CACHE_SECONDS:
        return hit[1]
    try:
        if source == "coinbase":
            c = parse_coinbase(_get_json(f"https://api.exchange.coinbase.com/products/{product}/candles",
                                         {"granularity": 60}))
        elif source == "kraken":
            c = parse_kraken(_get_json("https://api.kraken.com/0/public/OHLC", {"pair": KRAKEN[product], "interval": 1}))
        elif source == "bitstamp":
            c = parse_bitstamp(_get_json(f"https://www.bitstamp.net/api/v2/ohlc/{BITSTAMP[product]}/",
                                         {"step": 60, "limit": 120}))
        else:
            raise KeyError(source)
    except (KeyError, TypeError, ValueError):
        c = pd.Series(dtype=float)
    c = c[np.isfinite(c) & (c > 0)].sort_index() if len(c) else c
    _cache[key] = (time.monotonic(), c)
    return c


fetch = fetch_live  # tests replace this so no test ever reaches an exchange
SOURCES = ("coinbase", "kraken", "bitstamp")


def quote(product: str, now: pd.Timestamp, fetcher=None) -> tuple[list[float], float, str]:
    """(fresh closes, per-minute vol, note). No usable price -> ([], nan, why)."""
    fetcher = fetcher or fetch
    spots, vols, used = [], [], []
    for src in SOURCES:
        c = fetcher(src, product)
        c = c.sort_index() if len(c) else c              # Coinbase lists newest first; never trust the order
        c = c[c.index <= now] if len(c) else c          # only completed minutes: drops the one still forming
        if len(c) < MIN_BARS or now - c.index[-1] > STALE:
            continue
        v = float(np.log(c).diff().tail(60).std())
        if not np.isfinite(v) or v <= 0:
            continue
        spots.append(float(c.iloc[-1]))
        vols.append(v)
        used.append(src)
    if len(spots) < MIN_SOURCES:
        return [], np.nan, f"only {len(spots)} fresh source(s): {','.join(used) or 'none'}"
    med = float(np.median(spots))
    worst = max(abs(s / med - 1) for s in spots)
    if worst > DIVERGE:
        return [], np.nan, f"sources disagree by {worst:.2%}: " + " ".join(f"{u}={s:g}" for u, s in zip(used, spots))
    return spots, max(vols), ",".join(used)


def worst_z(z_sides, spots: list[float], vol: float, *args) -> tuple[float, float]:
    """The smallest (YES lead, NO lead) over every source's close: act only if all exchanges agree it's decided."""
    zs = [z_sides(*args[:3], s, vol, *args[3:]) for s in spots]
    if not zs:
        return np.nan, np.nan
    return min(z[0] for z in zs), min(z[1] for z in zs)
