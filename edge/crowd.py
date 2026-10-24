"""Round 4 family A: trade against retail positioning (Binance futures metrics).

`count_long_short_ratio` = long/short ratio of all accounts (dominated by
retail by count); `count_toptrader_long_short_ratio` = same for Binance's
largest accounts. Hourly bars; one position per coin at a time, held a
fixed number of hours; equal capital per coin.
"""
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from edge import data

COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
COST = 0.0007          # per side: 0.05% taker + 0.02% slippage
HOLDOUT_FROM = "2024-01-01"
ZWIN = 30 * 24         # 30-day z-score window, in hours


def _metrics(sym: str) -> pd.DataFrame:
    days = pd.date_range("2021-12-01", pd.Timestamp.utcnow().tz_localize(None).normalize()
                         - pd.Timedelta(days=2), freq="D")
    urls = [f"{data.VISION}/futures/um/daily/metrics/{sym}/{sym}-metrics-{d:%Y-%m-%d}.zip" for d in days]
    with ThreadPoolExecutor(24) as ex:
        parts = [p for p in ex.map(data._fetch_zip_csv, urls) if p is not None]
    if not parts:
        return pd.DataFrame()
    df = pd.concat(parts)
    out = pd.DataFrame({"retail": pd.to_numeric(df[6], errors="coerce").values,
                        "whale": pd.to_numeric(df[4], errors="coerce").values},
                       index=pd.to_datetime(df[0]).values)
    return out[~out.index.duplicated()].sort_index().resample("1h").last()


def _hourly_close(sym: str) -> pd.Series:
    base = f"{data.VISION}/futures/um/monthly/klines/{sym}/1h/{sym}-1h-"
    with ThreadPoolExecutor(16) as ex:
        parts = [p for p in ex.map(data._fetch_zip_csv, [f"{base}{m}.zip" for m in data._months("2021-11")])
                 if p is not None]
    df = pd.concat(parts)
    s = pd.Series(pd.to_numeric(df[4]).values, index=data._to_ts(df[0]).dt.tz_localize(None).values)
    return s[~s.index.duplicated()].sort_index()


def panel(refresh: bool = False) -> dict[str, pd.DataFrame]:
    path = data.CACHE / "crowd.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    out = {}
    for c in COINS:
        sym = f"{c}USDT"
        m, px, f = _metrics(sym), _hourly_close(sym), data._funding(sym)
        df = m.join(px.rename("close"), how="inner")
        df["funding_h"] = (f.reindex(df.index.normalize()).to_numpy() / 24)
        out[c] = df.dropna(subset=["close", "retail", "whale"])
        print(f"  {c}: {len(out[c])} hourly rows {out[c].index.min()} -> {out[c].index.max()}", flush=True)
    pd.to_pickle(out, path)
    return out


def _z(s):
    return (s - s.rolling(ZWIN, min_periods=ZWIN // 2).mean()) / s.rolling(ZWIN, min_periods=ZWIN // 2).std()


def _run_coin(df: pd.DataFrame, sig: np.ndarray, hold: int):
    """Enter at the next bar after a signal, hold `hold` hours, flat otherwise."""
    r = df["close"].pct_change().fillna(0).to_numpy()
    fund = np.nan_to_num(df["funding_h"].to_numpy())
    n = len(df)
    pos = np.zeros(n)
    trades = []
    i = 0
    while i < n - 1:
        if sig[i] != 0:
            d = sig[i]
            end = min(i + hold, n - 1)
            pos[i + 1:end + 1] = d
            gross = np.prod(1 + d * r[i + 1:end + 1]) - 1
            trades.append((df.index[i + 1], gross - 2 * COST - d * fund[i + 1:end + 1].sum()))
            i = end
        i += 1
    hourly = pos * r - pos * fund
    entries = np.diff(np.r_[0, pos]) != 0
    exits = np.diff(np.r_[pos, 0]) != 0
    hourly = hourly - COST * entries - COST * exits[:n]
    return pd.Series(hourly, index=df.index), trades


def _portfolio(p, make_sig, hold):
    daily, trades = [], []
    for c, df in p.items():
        h, t = _run_coin(df, make_sig(df), hold)
        daily.append(h.groupby(h.index.normalize()).sum().rename(c))
        trades += t
    d = pd.concat(daily, axis=1).fillna(0).mean(axis=1)  # equal capital per coin
    return d, pd.DataFrame(trades, columns=["time", "ret"])


def retail_fade(p, k, hold):
    def sig(df):
        z = _z(df["retail"]).to_numpy()
        return np.where(z > k, -1, np.where(z < -k, 1, 0))
    return _portfolio(p, sig, hold)


def follow_whales(p, hold):
    def sig(df):
        zw, zr = _z(df["whale"]).to_numpy(), _z(df["retail"]).to_numpy()
        disagree = (np.sign(zw) != np.sign(zr)) & (np.abs(zw - zr) > 2)
        return np.where(disagree, np.sign(zw), 0).astype(int)
    return _portfolio(p, sig, hold)


FAMILIES = {
    "retail_fade": (retail_fade, [dict(k=k, hold=h) for k in (1.5, 2.0) for h in (4, 24)]),
    "follow_whales": (follow_whales, [dict(hold=h) for h in (4, 24)]),
}
