"""Round 36 (PROTOCOL_ROUND36.md): retail-behavior anomaly battery on ~3,000 US stocks.
python run_round36.py data   -> data/r36/*.pkl
python run_round36.py run    -> reports/ROUND36.md"""
import io
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

D, OUT = Path("data/r36"), Path("reports/ROUND36.md")
DEV_END, HOLD_END = pd.Timestamp("2022-01-01"), pd.Timestamp("2026-12-01")
COST, BORROW_HOT, BORROW = 0.0010, 0.10, 0.05
SLOTS = 10


# ------------------------------------------------------------------ data
def universe() -> list[str]:
    out = []
    for url, sym, etf, test in (("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt", "Symbol", "ETF", "Test Issue"),
                                ("https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt", "ACT Symbol", "ETF", "Test Issue")):
        t = pd.read_csv(io.StringIO(requests.get(url, timeout=60).text), sep="|")
        t = t[(t[etf] == "N") & (t[test] == "N")]
        name = t["Security Name"].astype(str).str.lower()
        bad = name.str.contains("warrant|unit|right|preferred|depositary|notes|debenture|%|trust|fund|etn", regex=True)
        out += [s for s in t.loc[~bad, sym].astype(str) if s.isalpha() and len(s) <= 5]
    return sorted(set(out))


def data():
    import yfinance as yf
    D.mkdir(parents=True, exist_ok=True)
    tick = universe()
    print(f"universe: {len(tick)} tickers", flush=True)
    panels = {k: [] for k in ("Open", "Close", "Volume")}
    for i in range(0, len(tick), 200):
        chunk = tick[i:i + 200]
        for attempt in range(3):
            try:
                df = yf.download(chunk, start="2014-06-01", auto_adjust=True, progress=False, group_by="column", threads=True)
                break
            except Exception as e:
                print("retry", e, flush=True)
                time.sleep(10)
        else:
            continue
        for k in panels:
            if k in df:
                panels[k].append(df[k].astype("float32"))
        print(f"{i + len(chunk)}/{len(tick)}", flush=True)
    for k, parts in panels.items():
        p = pd.concat(parts, axis=1)
        p = p.loc[:, ~p.columns.duplicated()].dropna(axis=1, how="all")
        p.to_pickle(D / f"{k}.pkl")
        print(k, p.shape, flush=True)
    spy = yf.download("SPY", start="2014-06-01", auto_adjust=True, progress=False)
    if isinstance(spy.columns, pd.MultiIndex):
        spy.columns = spy.columns.get_level_values(0)
    spy.to_pickle(D / "SPY.pkl")


# ------------------------------------------------------------------ engines
def event_portfolio(O, C, sig: pd.DataFrame, side: int, H: int, borrow: float, rank: pd.DataFrame | None = None):
    """Signals at day t's close (bool frame) -> enter at day t+1's open, exit at the close of day t+H; 10 equal slots
    (each 10% of capital; idle slots earn 0). Returns (daily portfolio returns, per-trade net returns)."""
    dates = C.index
    o, c = O.to_numpy(), C.to_numpy()
    s = sig.to_numpy()
    rk = rank.to_numpy() if rank is not None else None
    n = len(dates)
    daily = np.zeros(n)
    active, trades = [], []          # active: [col, entry_idx, exit_idx]
    for d in range(1, n):
        keep = []
        for col, e, x in active:     # every active position earns day d's return
            prev = o[d, col] if d == e else c[d - 1, col]
            cur = c[d, col]
            r = side * (cur / prev - 1) if np.isfinite(prev) and np.isfinite(cur) and prev > 0 else 0.0
            daily[d] += r / SLOTS
            if side < 0:
                daily[d] -= borrow / 252 / SLOTS
            if d >= x:
                daily[d] -= COST / SLOTS
            else:
                keep.append([col, e, x])
        active = keep
        if d >= n - 1:
            continue
        free = SLOTS - len(active)
        if free <= 0:
            continue
        cols = np.where(s[d])[0]
        if not len(cols):
            continue
        if rk is not None:
            cols = cols[np.argsort(-np.nan_to_num(rk[d, cols]))]
        for col in cols[:free]:
            e, x = d + 1, min(d + H, n - 1)
            if not (np.isfinite(o[e, col]) and o[e, col] > 0):
                continue
            active.append([col, e, x])
            daily[e] -= COST / SLOTS
            ex = c[x, col]
            if np.isfinite(ex):
                trades.append((dates[d], side * (ex / o[e, col] - 1) - 2 * COST - (borrow * H / 252 if side < 0 else 0)))
    return pd.Series(daily, index=dates), pd.DataFrame(trades, columns=["date", "ret"])


def xsec_portfolio(C, score: pd.DataFrame, ok: pd.DataFrame, when: pd.DatetimeIndex, long_top: bool, legs: str = "ls",
                   q: float = 0.1, borrow: float = BORROW):
    """Rebalance on `when` dates (at the close): deciles of score among ok stocks. long_top: long the top decile.
    legs: 'ls' long-short (half capital each), 'short' short leg only, 'long' long leg only."""
    ret = C.pct_change(fill_method=None)
    daily = pd.Series(0.0, index=C.index)
    w_prev = pd.Series(dtype=float)
    reb = [d for d in when if d in C.index]
    for a, b in zip(reb, reb[1:] + [C.index[-1]]):
        sc = score.loc[a][ok.loc[a]].dropna()
        if len(sc) < 50:
            continue
        lo, hi = sc.quantile(q), sc.quantile(1 - q)
        top, bot = sc[sc >= hi].index, sc[sc <= lo].index
        long_, short_ = (top, bot) if long_top else (bot, top)
        w = pd.Series(0.0, index=sc.index)
        if legs in ("ls", "long"):
            w[long_] = (0.5 if legs == "ls" else 1.0) / len(long_)
        if legs in ("ls", "short"):
            w[short_] = -(0.5 if legs == "ls" else 1.0) / len(short_)
        w = w[w != 0]
        turn = w.subtract(w_prev, fill_value=0).abs().sum()
        period = ret.loc[(ret.index > a) & (ret.index <= b), w.index].fillna(0)
        pr = period.mul(w, axis=1).sum(axis=1) - (-w[w < 0]).sum() * borrow / 252
        if len(pr):
            pr.iloc[0] -= turn * COST
        daily.loc[pr.index] = pr
        w_prev = w
    return daily


def metrics(r: pd.Series) -> dict:
    r = r.dropna()
    if len(r) < 20 or r.std() == 0:
        return {"ann": 0.0, "sharpe": 0.0, "t": 0.0, "maxdd": 0.0}
    eq = (1 + r).cumprod()
    yrs = len(r) / 252
    return {"ann": float(eq.iloc[-1] ** (1 / yrs) - 1), "sharpe": float(r.mean() / r.std() * math.sqrt(252)),
            "t": float(r.mean() / (r.std() / math.sqrt(len(r)))), "maxdd": float((eq / eq.cummax() - 1).min())}


# ------------------------------------------------------------------ run
def run():
    O, C, V = (pd.read_pickle(D / f"{k}.pkl") for k in ("Open", "Close", "Volume"))
    cols = C.columns.intersection(O.columns).intersection(V.columns)
    O, C, V = O[cols].astype(float), C[cols].astype(float), V[cols].astype(float)
    spy = pd.read_pickle(D / "SPY.pkl")["Close"]
    C = C[C.index >= "2014-06-01"]
    O, V = O.reindex(C.index), V.reindex(C.index)
    dv20 = (C * V).rolling(20, min_periods=15).mean()
    ok = (C >= 3) & (dv20 >= 5e6)
    r1 = C.pct_change(fill_method=None)
    vr = V / V.rolling(50, min_periods=30).mean().shift(1)
    start = pd.Timestamp("2015-01-01")
    res = {}

    def ev(name, sig, side, H, borrow=0.0, rank=None):
        sig = sig.fillna(False) & (C.index >= start)[:, None]
        daily, tr = event_portfolio(O, C, sig, side, H, borrow, rank)
        res[name] = (daily, tr)
        print(name, len(tr), "trades", flush=True)

    frenzy = (r1 >= 0.20) & (vr >= 5) & ok
    panic = (r1 <= -0.20) & (vr >= 5) & ok
    for H in (1, 5, 20):
        ev(f"1 frenzy fade, short {H}d", frenzy, -1, H, BORROW_HOT, vr)
        ev(f"2 panic bounce, long {H}d", panic, +1, H, 0.0, vr)
    for H in (1, 5):
        ev(f"3 frenzy chase, long {H}d", frenzy, +1, H, 0.0, vr)
    gapup = (r1 >= 0.05) & (vr >= 3) & ok
    gapdn = (r1 <= -0.05) & (vr >= 3) & ok
    for H in (5, 20):
        ev(f"7 gap continuation up, long {H}d", gapup, +1, H, 0.0, vr)
        ev(f"7 gap continuation down, short {H}d", gapdn, -1, H, BORROW, vr)
    # 6 gap-up fade intraday: open >= +10/20% over prior close, short at open, cover at close (same day)
    gap = O / C.shift(1) - 1
    for g in (0.10, 0.20):
        sig = (gap >= g) & ok.shift(1).fillna(False) & (C.index >= start)[:, None]
        intr = -(C / O - 1) - 2 * COST - BORROW_HOT / 252
        x = intr.where(sig)
        n_per_day = sig.sum(axis=1).clip(upper=SLOTS)
        daily = (x.apply(lambda row: row.dropna().sort_values().iloc[:SLOTS].sum() if row.notna().any() else 0.0, axis=1) / SLOTS)
        tr = x.stack().reset_index()
        tr.columns = ["date", "ticker", "ret"]
        res[f"6 gap-up fade intraday >= {int(g*100)}%"] = (daily.fillna(0), tr[["date", "ret"]])
    # cross-sectional
    month_ends = C.index.to_series().groupby(C.index.to_period("M")).max()
    month_ends = pd.DatetimeIndex(month_ends[month_ends >= start])
    fridays = C.index.to_series().groupby(C.index.to_period("W-FRI")).max()
    fridays = pd.DatetimeIndex(fridays[fridays >= start])
    mx = r1.rolling(21, min_periods=15).max()
    res["4 MAX lottery, long low / short high"] = (xsec_portfolio(C, mx, ok, month_ends, long_top=False, legs="ls"), None)
    res["4 MAX lottery, short leg only"] = (xsec_portfolio(C, mx, ok, month_ends, long_top=False, legs="short", borrow=BORROW_HOT), None)
    hi52 = C / C.rolling(252, min_periods=200).max()
    res["5 52-week high, long near / short far"] = (xsec_portfolio(C, hi52, ok, month_ends, long_top=True, legs="ls"), None)
    r5 = C.pct_change(5, fill_method=None)
    res["8 weekly reversal, long losers / short winners"] = (xsec_portfolio(C, r5, ok, fridays, long_top=False, legs="ls"), None)
    penny_ok = (C >= 1) & (dv20 >= 1e6)
    score = -C.where(penny_ok)                      # high score = cheap
    res["9 penny stocks: short < $5 decile vs long the rest"] = (xsec_portfolio(C, score, penny_ok, month_ends, long_top=False, legs="ls", q=0.1), None)
    # 10 turn of month on SPY
    sp = spy.reindex(C.index).ffill()
    sr = sp.pct_change(fill_method=None)
    pos = pd.Series(0.0, index=C.index)
    idx = C.index
    for m_end in month_ends:
        i = idx.get_loc(m_end)
        pos.iloc[i + 1:i + 4] = 1.0                 # returns of the 1st-3rd trading days after holding from the last day's close
    tom = (sr * pos).fillna(0)
    chg = pos.diff().abs().fillna(0)
    res["10 turn of the month (SPY)"] = (tom - chg * COST, None)
    spym = {"dev": metrics(sr[(sr.index >= start) & (sr.index < DEV_END)]), "hold": metrics(sr[(sr.index >= DEV_END) & (sr.index < HOLD_END)])}
    rows = []
    for name, (daily, tr) in res.items():
        dv = metrics(daily[(daily.index >= start) & (daily.index < DEV_END)])
        ho = metrics(daily[(daily.index >= DEV_END) & (daily.index < HOLD_END)])
        n_tr = (len(tr[tr["date"] >= DEV_END]) if tr is not None and len(tr) else np.nan)
        avg = (tr[tr["date"] >= DEV_END]["ret"].mean() if tr is not None and len(tr) else np.nan)
        ok_ = dv["ann"] > 0 and ho["ann"] > 0 and ho["sharpe"] >= 1.0 and ho["t"] >= 3.0
        rows.append({"test": name, "dev %/yr": round(100 * dv["ann"], 1), "dev Sharpe": round(dv["sharpe"], 2),
                     "hold %/yr": round(100 * ho["ann"], 1), "hold Sharpe": round(ho["sharpe"], 2), "hold t": round(ho["t"], 2),
                     "hold worst drop": f"{ho['maxdd']:.0%}", "hold trades": n_tr,
                     "avg trade (net)": f"{avg:.2%}" if np.isfinite(avg) else "-",
                     "$25k/day": round(25000 * ho["ann"] / 365, 2), "PASS": "YES" if ok_ else ""})
    tab = pd.DataFrame(rows).sort_values("hold Sharpe", ascending=False)
    lines = ["# Round 36: beating retail traders' documented mistakes (US stocks)", "",
             "Rules: [PROTOCOL_ROUND36.md](../PROTOCOL_ROUND36.md). Next-open entry, 0.20% round trip, short borrow (10%/yr hot, 5% other). "
             f"Universe {C.shape[1]:,} stocks; dev 2015–2021, holdout 2022–2026. Survivorship bias: delisted stocks missing.", "",
             f"SPY buy-and-hold: dev {spym['dev']['ann']:.1%}/yr (Sharpe {spym['dev']['sharpe']:.2f}); holdout {spym['hold']['ann']:.1%}/yr "
             f"(Sharpe {spym['hold']['sharpe']:.2f}, worst drop {spym['hold']['maxdd']:.0%}).", "",
             f"**{(tab['PASS'] == 'YES').sum()} of {len(tab)} pass.**", "", tab.to_markdown(index=False)]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    {"data": data, "run": run}[sys.argv[1]]()
