"""Round 21 (PROTOCOL_ROUND21.md): 98-99c maker bids on crypto markets already decided by the spot price.

Kalshi's fixed-close crypto markets settle on a 60-second average of the CF Benchmarks index at close
versus a strike. At each long-shot fill (a taker buying one side at <= 2c) we look up the Binance
spot price from the last *completed* minute, and how many typical moves (z) it sits from the strike
given the minutes left. A fill counts for us only if the spot price says our side is winning by at
least Z. Our share is CAPTURE of each fill, capped at CAP contracts per market.
"""
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from edge import data as bdata
from edge import round20

CAPTURE, CAP = 0.25, 1000.0
SYMBOL = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT", "XRP": "XRPUSDT", "DOGE": "DOGEUSDT", "BNB": "BNBUSDT"}


def coin(series: str) -> str:
    return next(c for c in SYMBOL if series.startswith(f"KX{c}"))


def minutes(symbol: str, a: pd.Timestamp, b: pd.Timestamp) -> pd.Series:
    """Binance 1-minute closes, indexed by the minute's *close* time (UTC)."""
    months = pd.period_range(a.tz_convert(None), b.tz_convert(None), freq="M")
    base = f"{bdata.VISION}/spot/monthly/klines/{symbol}/1m/{symbol}-1m-"
    urls = [f"{base}{m}.zip" for m in months]
    days = pd.date_range(max(a, b - pd.Timedelta(days=40)).tz_convert(None).normalize(), b.tz_convert(None), freq="D")
    urls += [f"{bdata.VISION}/spot/daily/klines/{symbol}/1m/{symbol}-1m-{d:%Y-%m-%d}.zip" for d in days]
    with ThreadPoolExecutor(8) as ex:
        parts = [p for p in ex.map(bdata._fetch_zip_csv, urls) if p is not None]
    if not parts:
        return pd.Series(dtype=float)
    df = pd.concat(parts)
    s = pd.Series(pd.to_numeric(df[4]).to_numpy(), index=bdata._to_ts(df[0]) + pd.Timedelta(minutes=1))
    return s[~s.index.duplicated()].sort_index()


def zscores(spot: pd.Series, t: pd.Series, strike: float, close: pd.Timestamp) -> tuple[np.ndarray, np.ndarray]:
    """(spot from the last completed minute, signed z of log(spot/strike)) at each time in t."""
    logret = np.log(spot).diff()
    vol = logret.rolling(60, min_periods=30).std()  # per-minute volatility over the last hour
    idx = spot.index.searchsorted(t.to_numpy(), side="right") - 1
    ok = idx >= 0
    s = np.where(ok, spot.to_numpy()[np.clip(idx, 0, None)], np.nan)
    v = np.where(ok, vol.to_numpy()[np.clip(idx, 0, None)], np.nan)
    tau = np.maximum((close - t).dt.total_seconds().to_numpy() / 60, 0.5)  # settlement averages the final minute
    return s, np.log(s / strike) / (v * np.sqrt(tau))


def scan(series: str, a: pd.Timestamp, b: pd.Timestamp) -> pd.DataFrame:
    spot = minutes(SYMBOL[coin(series)], a - pd.Timedelta(days=1), b)
    print(f"  {series}: {len(spot):,} spot minutes ({spot.index.min()} .. {spot.index.max()})", flush=True)
    ms = sorted(round20.markets(series, a, b), key=lambda m: m.get("close_time", ""))
    weight = max(1, -(-len(ms) // round20.MAX_MARKETS))
    ms = [m for m in ms[::weight] if m.get("strike_type") in ("greater", "greater_or_equal")]
    print(f"  {series}: testing {len(ms)} markets (every {weight})", flush=True)
    with ThreadPoolExecutor(4) as ex:
        trs = list(ex.map(lambda m: round20.r15.trades(m["ticker"]), ms))
    rows = []
    for m, tr in zip(ms, trs):
        f = round20.fills(m, tr)
        if f.empty:
            continue
        close = pd.to_datetime(m["close_time"], utc=True)
        f = f.sort_values("time")
        s, z = zscores(spot, f["time"], float(m["floor_strike"]), close)
        maker = np.where(f["taker_side"] == "yes", "no", "yes")
        f["spot"], f["z_for_us"] = s, np.where(maker == "yes", z, -z)  # > 0: spot says our side is winning
        f["result"] = m["result"]
        f["weight"] = weight
        rows.append(f)
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    if len(out):
        out["series"] = series
    print(f"  {series}: {len(out):,} long-shot fills; long shots won {int(out['won_longshot'].sum()) if len(out) else 0}", flush=True)
    return out


def book(f: pd.DataFrame, zmin: float) -> pd.DataFrame:
    """Fills we take at threshold zmin: CAPTURE share, capped at CAP contracts per market, maker fee per fill."""
    f = f[f["z_for_us"] >= zmin].sort_values("time").copy()
    if f.empty:
        return f
    want = f["count"] * CAPTURE
    before = want.groupby(f["ticker"]).cumsum() - want
    n = np.clip(CAP - before, 0, None).clip(upper=want)
    fee = np.array([round20.r15._maker_fee(x, 1 - p) if x > 0 else 0.0 for x, p in zip(n, f["px"])])
    f["n"] = n
    f["pnl"] = (np.where(f["won_longshot"], -(1 - f["px"]) * n, f["px"] * n) - fee) * f["weight"]
    return f
