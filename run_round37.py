"""Round 37 (PROTOCOL_ROUND37.md): retail-behavior battery on all Binance USDT pairs (daily)."""
import io
import re
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

import run_round36 as R

D, OUT = Path("data/r37"), Path("reports/ROUND37.md")
DEV_END, HOLD_END = pd.Timestamp("2023-01-01"), pd.Timestamp("2026-11-01")
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
VISION = "https://data.binance.vision/data/spot/monthly/klines"
STABLE = {"USDC", "BUSD", "TUSD", "PAX", "USDP", "DAI", "FDUSD", "EUR", "GBP", "AUD", "UST", "USDS", "SUSD", "AEUR", "EURI", "XUSD", "USD1"}


def pairs() -> list[str]:
    out, marker = [], ""
    while True:
        r = requests.get(S3, params={"prefix": "data/spot/monthly/klines/", "delimiter": "/", "marker": marker}, timeout=60)
        names = re.findall(r"<Prefix>data/spot/monthly/klines/([A-Z0-9]+)/</Prefix>", r.text)
        out += names
        if "<IsTruncated>true</IsTruncated>" not in r.text or not names:
            break
        marker = f"data/spot/monthly/klines/{names[-1]}/"
    keep = []
    for p in out:
        if not p.endswith("USDT"):
            continue
        base = p[:-4]
        if base in STABLE or re.search(r"(UP|DOWN|BULL|BEAR)$", base):
            continue
        keep.append(p)
    return sorted(set(keep))


def one(sym: str) -> pd.DataFrame | None:
    months = pd.period_range("2018-01", "2026-10", freq="M")
    parts = []
    for m in months:
        url = f"{VISION}/{sym}/1d/{sym}-1d-{m}.zip"
        try:
            r = requests.get(url, timeout=30)
        except requests.RequestException:
            continue
        if r.status_code != 200:
            continue
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            df = pd.read_csv(z.open(z.namelist()[0]), header=None)
        parts.append(df)
    if not parts:
        return None
    df = pd.concat(parts)
    t = pd.to_numeric(df[0])
    t = np.where(t > 1e14, t // 1000, t)                 # some archives switched to microseconds
    idx = pd.to_datetime(t, unit="ms").normalize()
    out = pd.DataFrame({"Open": pd.to_numeric(df[1]).values, "Close": pd.to_numeric(df[4]).values,
                        "Volume": pd.to_numeric(df[7]).values}, index=idx)   # col 7 = quote (USDT) volume
    return out[~out.index.duplicated()].sort_index()


def data():
    D.mkdir(parents=True, exist_ok=True)
    ps = pairs()
    print(f"{len(ps)} USDT pairs", flush=True)
    frames = {}
    with ThreadPoolExecutor(8) as ex:
        for sym, df in zip(ps, ex.map(one, ps)):
            if df is not None and len(df) > 30:
                frames[sym] = df
    for k in ("Open", "Close", "Volume"):
        pd.DataFrame({s: f[k] for s, f in frames.items()}).sort_index().to_pickle(D / f"{k}.pkl")
    print("saved", len(frames), flush=True)


def run():
    O, C, Vq = (pd.read_pickle(D / f"{k}.pkl").astype(float) for k in ("Open", "Close", "Volume"))
    R.DEV_END, R.HOLD_END = DEV_END, HOLD_END
    dv20 = Vq.rolling(20, min_periods=10).mean()
    ok = dv20 >= 2e6
    r1 = C.pct_change(fill_method=None)
    vr = Vq / Vq.rolling(50, min_periods=20).mean().shift(1)
    start = pd.Timestamp("2019-01-01")
    res = {}

    def ev(name, sig, side, H, borrow=0.0, rank=None):
        sig = sig.fillna(False) & (C.index >= start)[:, None]
        res[name] = R.event_portfolio(O, C, sig, side, H, borrow, rank)
        print(name, len(res[name][1]), "trades", flush=True)

    for th in (0.20, 0.30):
        pump = (r1 >= th) & (vr >= 5) & ok
        for H in (1, 3, 7):
            ev(f"1 pump fade >= {int(th*100)}%, short {H}d", pump, -1, H, R.BORROW_HOT, vr)
    dump = (r1 <= -0.20) & (vr >= 5) & ok
    for H in (1, 3, 7):
        ev(f"2 dump bounce, long {H}d", dump, +1, H, 0.0, vr)
    first = C.notna().cumsum()
    newl = (first == 3) & (C.index >= start)[:, None]           # signal at the close of day 3 -> short days 4..30
    ev("3 new-listing fade, short days 4-30", newl, -1, 27, R.BORROW_HOT)
    weeks = C.index.to_series().groupby(C.index.to_period("W-SUN")).max()
    weeks = pd.DatetimeIndex(weeks[weeks >= start])
    res["4 weekly reversal, long losers / short winners"] = (R.xsec_portfolio(C, C.pct_change(7, fill_method=None), ok, weeks, long_top=False, legs="ls", borrow=R.BORROW_HOT), None)
    res["5 momentum 30d, long winners / short losers"] = (R.xsec_portfolio(C, C.pct_change(30, fill_method=None), ok, weeks, long_top=True, legs="ls", borrow=R.BORROW_HOT), None)
    btc = C["BTCUSDT"]
    br = btc.pct_change(fill_method=None)
    wk = pd.Series(np.where(br.index.dayofweek.isin([5, 6]), 1.0, 0.0), index=br.index)   # Sat and Sun daily returns
    res["6 BTC weekend (Fri close -> Sun close)"] = ((br * wk).fillna(0) - wk.diff().abs().fillna(0) * R.COST, None)
    rows = []
    for name, (daily, tr) in res.items():
        dv = R.metrics(daily[(daily.index >= start) & (daily.index < DEV_END)] * np.sqrt(252 / 365) ** 0)
        ho = R.metrics(daily[(daily.index >= DEV_END) & (daily.index < HOLD_END)])
        n_tr = len(tr[tr["date"] >= DEV_END]) if tr is not None and len(tr) else np.nan
        avg = tr[tr["date"] >= DEV_END]["ret"].mean() if tr is not None and len(tr) else np.nan
        ok_ = dv["ann"] > 0 and ho["ann"] > 0 and ho["sharpe"] >= 1.0 and ho["t"] >= 3.0
        rows.append({"test": name, "dev %/yr": round(100 * dv["ann"], 1), "dev Sharpe": round(dv["sharpe"], 2),
                     "hold %/yr": round(100 * ho["ann"], 1), "hold Sharpe": round(ho["sharpe"], 2), "hold t": round(ho["t"], 2),
                     "hold worst drop": f"{ho['maxdd']:.0%}", "hold trades": n_tr,
                     "avg trade (net)": f"{avg:.2%}" if np.isfinite(avg) else "-", "PASS": "YES" if ok_ else ""})
    tab = pd.DataFrame(rows).sort_values("hold Sharpe", ascending=False)
    lines = ["# Round 37: beating retail crypto traders (all Binance USDT pairs)", "",
             "Rules: [PROTOCOL_ROUND37.md](../PROTOCOL_ROUND37.md). Crypto trades 365 days a year; annualisation uses 252 "
             "steps for comparability with stocks, so Sharpe/annual figures are slightly understated.", "",
             f"Pairs: {C.shape[1]:,}. **{(tab['PASS'] == 'YES').sum()} of {len(tab)} pass.**", "", tab.to_markdown(index=False)]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    {"data": data, "run": run}[sys.argv[1]]()
