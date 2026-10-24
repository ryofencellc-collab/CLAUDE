"""Data loaders. Everything is cached to data/ as parquet/csv.

Sources (all free, no keys):
  * Binance public archive (data.binance.vision): spot + USD-M perp daily
    klines and perp funding rates. Includes coins later delisted, which
    reduces survivorship bias.
  * Yahoo Finance via yfinance: US ETFs and volatility indices.
"""
import io
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

CACHE = Path(__file__).resolve().parent.parent / "data"
CACHE.mkdir(exist_ok=True)
VISION = "https://data.binance.vision/data"

# Fixed universe, chosen for "was a large coin at some point since 2018",
# deliberately including names that later collapsed or were delisted.
CRYPTO_UNIVERSE = [
    "BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "DOT", "LTC", "LINK",
    "BCH", "TRX", "EOS", "XLM", "ATOM", "ETC", "XMR", "LUNA", "FTT", "AVAX",
    "MATIC", "UNI", "FIL", "VET", "ALGO", "NEO", "IOTA", "ZEC", "DASH", "XTZ",
]

_session = requests.Session()


def _months(start="2017-08", end=None):
    end = end or (pd.Timestamp.utcnow() - pd.offsets.MonthBegin(1)).strftime("%Y-%m")
    return [p.strftime("%Y-%m") for p in pd.period_range(start, end, freq="M")]


def _fetch_zip_csv(url: str) -> pd.DataFrame | None:
    try:
        resp = _session.get(url, timeout=30)
    except requests.RequestException:
        return None
    if resp.status_code != 200:
        return None
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        raw = z.read(z.namelist()[0]).decode()
    df = pd.read_csv(io.StringIO(raw), header=None)
    if not str(df.iloc[0, 0]).lstrip("-").isdigit():  # some files have a header row
        df = df.iloc[1:]
    return df


def _to_ts(col: pd.Series) -> pd.Series:
    v = pd.to_numeric(col)
    # archive switched from ms to us timestamps in 2025
    v = v.where(v < 1e14, v // 1000)
    return pd.to_datetime(v, unit="ms", utc=True)


def _klines(market: str, symbol: str) -> pd.DataFrame:
    base = f"{VISION}/{market}/monthly/klines/{symbol}/1d/{symbol}-1d-"
    urls = [f"{base}{m}.zip" for m in _months()]
    with ThreadPoolExecutor(16) as ex:
        parts = [p for p in ex.map(_fetch_zip_csv, urls) if p is not None]
    if not parts:
        return pd.DataFrame()
    df = pd.concat(parts)
    out = pd.DataFrame({
        "open": pd.to_numeric(df[1]).values,
        "close": pd.to_numeric(df[4]).values,
        "quote_volume": pd.to_numeric(df[7]).values,
    }, index=_to_ts(df[0]).dt.normalize().dt.tz_localize(None))
    return out[~out.index.duplicated()].sort_index()


def _funding(symbol: str) -> pd.Series:
    base = f"{VISION}/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-"
    urls = [f"{base}{m}.zip" for m in _months("2019-09")]
    with ThreadPoolExecutor(16) as ex:
        parts = [p for p in ex.map(_fetch_zip_csv, urls) if p is not None]
    if not parts:
        return pd.Series(dtype=float)
    df = pd.concat(parts)
    s = pd.Series(pd.to_numeric(df[2]).values,
                  index=_to_ts(df[0]).dt.tz_localize(None))
    # daily sum of funding payments (positive = longs pay shorts)
    return s.groupby(s.index.normalize()).sum().sort_index()


def crypto_panel(refresh: bool = False) -> dict[str, pd.DataFrame]:
    """Returns dict of wide DataFrames: spot_close, spot_qv, perp_close, funding."""
    path = CACHE / "crypto.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    spot, qv, perp, fund = {}, {}, {}, {}
    for c in CRYPTO_UNIVERSE:
        sym = f"{c}USDT"
        k = _klines("spot", sym)
        if not k.empty:
            spot[c], qv[c] = k["close"], k["quote_volume"]
        p = _klines("futures/um", sym)
        if not p.empty:
            perp[c] = p["close"]
        f = _funding(sym)
        if not f.empty:
            fund[c] = f
        print(f"  {c}: spot={len(k)} perp={len(p)} funding={len(f)}", flush=True)
    panel = {
        "spot_close": pd.DataFrame(spot),
        "spot_qv": pd.DataFrame(qv),
        "perp_close": pd.DataFrame(perp),
        "funding": pd.DataFrame(fund),
    }
    pd.to_pickle(panel, path)
    return panel


ETF_TICKERS = ["SPY", "QQQ", "IWM", "TLT", "GLD", "SVXY", "VXX", "^VIX", "^VIX3M", "^IRX"]


def etf_panel(refresh: bool = False) -> dict[str, pd.DataFrame]:
    """Adjusted open/close for ETFs and index levels. ^IRX = 13w T-bill yield."""
    path = CACHE / "etf.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    import yfinance as yf
    raw = yf.download(ETF_TICKERS, start="2000-01-01", auto_adjust=True,
                      progress=False, group_by="column")
    panel = {"open": raw["Open"], "close": raw["Close"]}
    pd.to_pickle(panel, path)
    return panel
