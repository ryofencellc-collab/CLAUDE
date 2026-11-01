"""Round 24 (PROTOCOL_ROUND24.md): 99c maker bids on Kalshi S&P 500 / Nasdaq-100 binary options already decided
by the index level. Round 21's method with index data: 5-minute bars from Yahoo (the last 60 days is all Yahoo
serves at that resolution), each bar known only once it has closed.
"""
import numpy as np
import pandas as pd

from edge import round20, round21

INDEX = {"KXINXU": "^GSPC", "KXINX": "^GSPC", "KXNASDAQ100U": "^NDX", "KXNASDAQ100": "^NDX"}
STALE = pd.Timedelta(minutes=10)  # outside regular hours there is no fresh bar: no z, no fill counted


def bars(ticker: str) -> pd.Series:
    """5-minute closes indexed by the bar's close time (UTC)."""
    import yfinance as yf
    df = yf.download(ticker, period="60d", interval="5m", progress=False, auto_adjust=False)
    if df.empty:
        return pd.Series(dtype=float)
    c = df["Close"]
    c = c.iloc[:, 0] if isinstance(c, pd.DataFrame) else c
    idx = c.index.tz_convert("UTC") if c.index.tz is not None else c.index.tz_localize("UTC")
    return pd.Series(c.to_numpy(dtype=float), index=idx + pd.Timedelta(minutes=5)).dropna().sort_index()


def z_side(m: dict, spot: pd.Series, t: pd.Series, close: pd.Timestamp):
    """Per time in t: (z for YES winning, z for NO winning); the larger positive one names the decided side."""
    logret = np.log(spot).diff()
    vol = logret.rolling(12, min_periods=6).std() / np.sqrt(5)  # per-minute vol over the last hour
    idx = spot.index.searchsorted(t.to_numpy(), side="right") - 1
    ok = idx >= 0
    j = np.clip(idx, 0, None)
    s = np.where(ok, spot.to_numpy()[j], np.nan)
    v = np.where(ok, vol.to_numpy()[j], np.nan)
    fresh = ok & ((t.to_numpy() - spot.index.to_numpy()[j]) <= STALE.to_timedelta64())
    tau = np.maximum((close - t).dt.total_seconds().to_numpy() / 60, 0.5)
    den = v * np.sqrt(tau)
    f = pd.to_numeric(m.get("floor_strike"), errors="coerce")
    c = pd.to_numeric(m.get("cap_strike"), errors="coerce")
    st = m.get("strike_type")
    with np.errstate(divide="ignore", invalid="ignore"):
        if st in ("greater", "greater_or_equal"):
            zy = np.log(s / f) / den
            zn = -zy
        elif st in ("less", "less_or_equal"):
            zy = np.log(c / s) / den
            zn = -zy
        elif st == "between":
            inside = np.minimum(np.log(s / f), np.log(c / s)) / den    # > 0: inside the range
            zy, zn = inside, -inside                                      # NO wins when far outside
        else:
            zy = zn = np.full(len(t), np.nan)
    zy = np.where(fresh, zy, np.nan)
    zn = np.where(fresh, zn, np.nan)
    return s, zy, zn


def scan(series: str, a: pd.Timestamp, b: pd.Timestamp, spot: pd.Series) -> pd.DataFrame:
    ms = sorted(round20.markets(series, a, b), key=lambda m: m.get("close_time", ""))
    weight = max(1, -(-len(ms) // round20.MAX_MARKETS))
    ms = ms[::weight]
    print(f"  {series}: {len(ms)} markets (every {weight}); spot bars {len(spot):,} "
          f"({spot.index.min()} .. {spot.index.max()})", flush=True)
    rows = []
    for m in ms:
        f = round20.fills(m, round20.r15.trades(m["ticker"]))
        if f.empty:
            continue
        close = pd.to_datetime(m["close_time"], utc=True)
        f = f.sort_values("time")
        s, zy, zn = z_side(m, spot, f["time"], close)
        maker = np.where(f["taker_side"] == "yes", "no", "yes")
        f["spot"], f["z_for_us"] = s, np.where(maker == "yes", zy, zn)
        f["result"], f["weight"], f["series"] = m["result"], weight, series
        rows.append(f)
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    print(f"  {series}: {len(out):,} long-shot fills, {int(out['won_longshot'].sum()) if len(out) else 0} long shots won, "
          f"{int(out['z_for_us'].notna().sum()) if len(out) else 0} with a fresh index bar", flush=True)
    return out


book = round21.book
