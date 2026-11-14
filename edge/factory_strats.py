"""Strategy registry for the factory. Each entry: name -> (market, batch, fn(data) -> weights DataFrame).
Batch 1 added 2026-11-13 (before running): classic documented anomalies and rotations not yet tested here."""
from __future__ import annotations
import numpy as np, pandas as pd

REG: dict = {}


def strat(name, market, batch):
    def deco(fn):
        REG[name] = (market, batch, fn)
        return fn
    return deco


def month_end_mask(idx):
    s = pd.Series(idx, index=idx)
    return s.groupby([idx.year, idx.month]).transform("max") == s


def topk_monthly(score: pd.DataFrame, ok: pd.DataFrame, frac=0.1, k=None, largest=True, every="M", min_n=20):
    mask = month_end_mask(score.index) if every == "M" else (score.index.weekday == 4)
    sc = score.where(ok)
    w = pd.DataFrame(np.nan, index=score.index, columns=score.columns)
    for t in score.index[mask]:
        row = sc.loc[t].dropna()
        if len(row) < min_n:
            v = pd.Series(0.0, index=score.columns); w.loc[t] = v      # too few candidates: hold cash this period
            continue
        n = k or max(1, int(len(row) * frac))
        pick = row.nlargest(n).index if largest else row.nsmallest(n).index
        v = pd.Series(0.0, index=score.columns); v[pick] = 1.0 / n
        w.loc[t] = v
    return w.ffill().fillna(0.0)


# ------------------------------------------------------------ stocks (cross-sectional, long-only, top decile)
@strat("XS momentum 12-1 (top 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"].shift(21) / d["C"].shift(252) - 1, d["ok"])

@strat("XS momentum 6-1 (top 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"].shift(21) / d["C"].shift(126) - 1, d["ok"])

@strat("Short-term reversal (weekly losers, 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"] / d["C"].shift(5) - 1, d["ok"], largest=False, every="W")

@strat("Low volatility (lowest 10% 60d vol)", "stocks", 1)
def _(d): return topk_monthly(d["C"].pct_change(fill_method=None).rolling(60).std(), d["ok"], largest=False)

@strat("52-week-high proximity (top 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"] / d["C"].rolling(252).max(), d["ok"])

@strat("Anti-lottery (lowest monthly max daily return, 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"].pct_change(fill_method=None).rolling(21).max(), d["ok"], largest=False)

@strat("Momentum + low vol (rank sum, top 10%)", "stocks", 1)
def _(d):
    m = (d["C"].shift(21) / d["C"].shift(252) - 1).rank(axis=1, pct=True)
    v = d["C"].pct_change(fill_method=None).rolling(60).std().rank(axis=1, pct=True, ascending=False)
    return topk_monthly(m + v, d["ok"])

@strat("Momentum 12-1, top 20 names only", "stocks", 1)
def _(d): return topk_monthly(d["C"].shift(21) / d["C"].shift(252) - 1, d["ok"], k=20)


# ------------------------------------------------------------ ETFs / SPY
def one(d, col, pos):  # pos: Series of target weight for one ticker
    w = pd.DataFrame(0.0, index=d["E"].index, columns=d["E"].columns); w[col] = pos.reindex(w.index).fillna(0.0); return w

@strat("Turn-of-month SPY (last 4 + first 3 days)", "etfs", 1)
def _(d):
    idx = d["E"].index; s = pd.Series(range(len(idx)), index=idx)
    g = s.groupby([idx.year, idx.month]); pos_in = s - g.transform("min"); pos_end = g.transform("max") - s
    # weight decided at t applies from t+1's close... so mark the day before the window
    win = ((pos_in <= 2) | (pos_end <= 3)).astype(float).shift(-2).fillna(0)
    return one(d, "SPY", win)

@strat("Sell in May: SPY Nov-Apr, IEF May-Oct", "etfs", 1)
def _(d):
    idx = d["E"].index; w = pd.DataFrame(0.0, index=idx, columns=d["E"].columns)
    winter = pd.Series(idx.month.isin([11, 12, 1, 2, 3, 4]), index=idx).astype(float)
    w["SPY"], w["IEF"] = winter, 1 - winter; return w

@strat("Dual momentum GEM (SPY/EFA by 12m, else AGG)", "etfs", 1)
def _(d):
    E = d["E"]; r12 = E / E.shift(252) - 1; me = month_end_mask(E.index)
    w = pd.DataFrame(np.nan, index=E.index, columns=E.columns)
    for t in E.index[me]:
        v = pd.Series(0.0, index=E.columns)
        if r12.loc[t, ["SPY", "EFA"]].isna().any(): continue
        best = "SPY" if r12.loc[t, "SPY"] >= r12.loc[t, "EFA"] else "EFA"
        v["AGG" if r12.loc[t, "SPY"] < r12.loc[t, "BIL"] else best] = 1.0
        w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Sector rotation (top 3 SPDR sectors by 3m return)", "etfs", 1)
def _(d):
    secs = [c for c in ("XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLB", "XLU", "XLRE", "XLC") if c in d["E"].columns]
    sc = (d["E"][secs] / d["E"][secs].shift(63) - 1)
    me = month_end_mask(sc.index); w = pd.DataFrame(np.nan, index=sc.index, columns=d["E"].columns)
    for t in sc.index[me]:
        row = sc.loc[t].dropna()
        if len(row) < 5: continue
        v = pd.Series(0.0, index=d["E"].columns); v[row.nlargest(3).index] = 1 / 3; w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Volatility-managed SPY (15% vol target, max 1.5x)", "etfs", 1)
def _(d):
    r = d["E"]["SPY"].pct_change(fill_method=None); vol = r.rolling(21).std() * np.sqrt(252)
    return one(d, "SPY", (0.15 / vol).clip(upper=1.5))

@strat("2x SPY above 200-day average, else cash", "etfs", 1)
def _(d):
    s = d["E"]["SPY"]; return one(d, "SPY", 2.0 * (s > s.rolling(200).mean()).astype(float))

@strat("SPY above 200-day average, else IEF", "etfs", 1)
def _(d):
    s = d["E"]["SPY"]; up = (s > s.rolling(200).mean()).astype(float)
    w = one(d, "SPY", up); w["IEF"] = 1 - up; return w


# ------------------------------------------------------------ crypto
@strat("Crypto XS momentum: top 5 of 30 by 30d return, weekly", "crypto", 1)
def _(d): return topk_monthly(d["X"] / d["X"].shift(30) - 1, d["X"].notna() & d["X"].shift(60).notna(), k=5, every="W")

@strat("Crypto: BTC+ETH 50/200 golden cross, else cash", "crypto", 1)
def _(d):
    X = d["X"][["BTC", "ETH"]]; on = (X.rolling(50).mean() > X.rolling(200).mean()).astype(float) / 2
    return on.reindex(columns=d["X"].columns, fill_value=0.0)


# ============================================================ batch 2 (registered 2026-11-14, before running): stock anomalies
def _mret(d):
    r = d["C"].pct_change(fill_method=None)
    m = r.where(d["ok"].shift(1, fill_value=False)).mean(axis=1)
    return r, m


@strat("Low idiosyncratic volatility (residual vs market, 60d, lowest 10%)", "stocks", 2)
def _(d):
    r, m = _mret(d)
    return topk_monthly(r.sub(m, axis=0).rolling(60, min_periods=40).std(), d["ok"], largest=False)

@strat("Betting-against-beta long leg (lowest 60d beta, 10%)", "stocks", 2)
def _(d):
    r, m = _mret(d)
    cov = (r.mul(m, axis=0)).rolling(60, min_periods=40).mean() - r.rolling(60, min_periods=40).mean().mul(m.rolling(60, min_periods=40).mean(), axis=0)
    beta = cov.div(m.rolling(60, min_periods=40).var(ddof=0), axis=0)
    return topk_monthly(beta, d["ok"], largest=False)

@strat("Time-series momentum: top-200 liquid with 12m return > 0", "stocks", 2)
def _(d):
    r12 = d["C"] / d["C"].shift(252) - 1
    me = month_end_mask(d["C"].index); w = pd.DataFrame(np.nan, index=d["C"].index, columns=d["C"].columns)
    for t in d["C"].index[me]:
        liq = d["dv"].loc[t].where(d["ok"].loc[t]).dropna().nlargest(200).index
        pick = [c for c in liq if r12.at[t, c] > 0]
        v = pd.Series(0.0, index=d["C"].columns)
        if pick: v[pick] = 1.0 / len(pick)
        w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Overnight-return momentum (21d sum of open/prior-close, top 10%)", "stocks", 2)
def _(d):
    on = np.log(d["O"] / d["C"].shift(1)).rolling(21, min_periods=15).sum()
    return topk_monthly(on, d["ok"])

@strat("Volume-shock reversal (down >= 3% on 3x volume, hold 5 days)", "stocks", 2)
def _(d):
    r = d["C"].pct_change(fill_method=None)
    sig = (r <= -0.03) & (d["V"] >= 3 * d["V"].rolling(50, min_periods=30).mean().shift(1)) & d["ok"]
    act = sig.astype(float).rolling(5, min_periods=1).max()
    return act.div(act.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)

@strat("Same-month seasonality (Heston-Sadka, 5y, top 10%)", "stocks", 2)
def _(d):
    mc = d["C"].resample("ME").last(); mr = mc.pct_change(fill_method=None)
    score_m = sum(mr.shift(k) for k in (11, 23, 35, 47, 59)) / 5      # same month in past years, for next month
    score = score_m.reindex(d["C"].index, method="ffill")
    return topk_monthly(score, d["ok"])

@strat("Liquidity premium (least liquid 10% of tradable set)", "stocks", 2)
def _(d): return topk_monthly(d["dv"], d["ok"], largest=False)


# ============================================================ batch 3 (registered 2026-11-14, before running): ETFs / macro
def _inv_vol_weights(E, names, lev=1.0):
    r = E[names].pct_change(fill_method=None); iv = 1 / r.rolling(63, min_periods=40).std()
    me = month_end_mask(E.index); w = pd.DataFrame(np.nan, index=E.index, columns=E.columns)
    for t in E.index[me]:
        x = iv.loc[t].dropna()
        if len(x) < len(names): continue
        v = pd.Series(0.0, index=E.columns); v[x.index] = lev * x / x.sum(); w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Risk parity SPY/TLT/GLD/DBC (inverse vol, monthly)", "etfs", 3)
def _(d): return _inv_vol_weights(d["E"], ["SPY", "TLT", "GLD", "DBC"])

@strat("Risk parity SPY/TLT/GLD/DBC at 1.5x", "etfs", 3)
def _(d): return _inv_vol_weights(d["E"], ["SPY", "TLT", "GLD", "DBC"], 1.5)

@strat("Canary (DAA-style): SPY/EFA/EEM momentum unless VWO or BND canary negative -> IEF", "etfs", 3)
def _(d):
    E = d["E"]
    def m13612(x): return (12 * (x / x.shift(21) - 1) + 4 * (x / x.shift(63) - 1) + 2 * (x / x.shift(126) - 1) + (x / x.shift(252) - 1))
    mom = m13612(E); me = month_end_mask(E.index); w = pd.DataFrame(np.nan, index=E.index, columns=E.columns)
    for t in E.index[me]:
        if mom.loc[t, ["VWO", "BND", "SPY", "EFA", "EEM"]].isna().any(): continue
        v = pd.Series(0.0, index=E.columns)
        if (mom.loc[t, ["VWO", "BND"]] < 0).any(): v["IEF"] = 1.0
        else: v[mom.loc[t, ["SPY", "EFA", "EEM"]].idxmax()] = 1.0
        w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Stock/bond switch: SPY or TLT by 3m momentum", "etfs", 3)
def _(d):
    E = d["E"]; m = E[["SPY", "TLT"]] / E[["SPY", "TLT"]].shift(63) - 1; me = month_end_mask(E.index)
    w = pd.DataFrame(np.nan, index=E.index, columns=E.columns)
    for t in E.index[me]:
        if m.loc[t].isna().any(): continue
        v = pd.Series(0.0, index=E.columns); v[m.loc[t].idxmax()] = 1.0; w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("VIX term structure: SPY when VIX < VIX3M, else IEF", "etfs", 3)
def _(d):
    E = d["E"]; on = (E["^VIX"] < E["^VIX3M"]).astype(float).where(E[["^VIX", "^VIX3M"]].notna().all(axis=1))
    on = on.ffill().fillna(0.0); w = one(d, "SPY", on); w["IEF"] = 1 - on; return w

@strat("Pre-holiday SPY (day before US market holidays)", "etfs", 3)
def _(d):
    from pandas.tseries.holiday import USFederalHolidayCalendar
    idx = d["E"].index; hol = USFederalHolidayCalendar().holidays(idx[0], idx[-1] + pd.Timedelta(days=10))
    nxt = pd.Series(idx[1:].tolist() + [idx[-1] + pd.Timedelta(days=1)], index=idx)
    pre = pd.Series([(n - t).days > 1 and any((h > t) and (h < n) for h in hol[(hol > t) & (hol < n)]) for t, n in nxt.items()], index=idx)
    return one(d, "SPY", pre.astype(float).shift(-2).fillna(0.0))   # weight at t earns t+1 -> t+2: mark 2 days ahead


# ============================================================ batch 4 (registered 2026-11-14 03:20 UTC, before running): crypto
def _xone(d, col, pos):
    w = pd.DataFrame(0.0, index=d["X"].index, columns=d["X"].columns); w[col] = pos.reindex(w.index).fillna(0.0); return w

@strat("Crypto alt/BTC rotation: top-5 alts when alts beat BTC over 30d, else BTC (weekly)", "crypto", 4)
def _(d):
    X = d["X"]; r30 = X / X.shift(30) - 1; fri = X.index.weekday == 4
    w = pd.DataFrame(np.nan, index=X.index, columns=X.columns)
    for t in X.index[fri]:
        alts = r30.loc[t].drop("BTC").dropna()
        if len(alts) < 10 or pd.isna(r30.at[t, "BTC"]): continue
        v = pd.Series(0.0, index=X.columns)
        if alts.median() > r30.at[t, "BTC"]: v[alts.nlargest(5).index] = 0.2
        else: v["BTC"] = 1.0
        w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Crypto low volatility: 5 lowest 30d-vol coins, weekly", "crypto", 4)
def _(d):
    X = d["X"]; return topk_monthly(X.pct_change(fill_method=None).rolling(30, min_periods=25).std(), X.notna() & X.shift(60).notna(), k=5, largest=False, every="W")

@strat("Crypto 7-day losers (5 worst), weekly", "crypto", 4)
def _(d):
    X = d["X"]; return topk_monthly(X / X.shift(7) - 1, X.notna() & X.shift(60).notna(), k=5, largest=False, every="W")

@strat("BTC volatility target 40% (max 1x)", "crypto", 4)
def _(d):
    r = d["X"]["BTC"].pct_change(fill_method=None); vol = r.rolling(30).std() * np.sqrt(365)
    return _xone(d, "BTC", (0.40 / vol).clip(upper=1.0))

@strat("BTC 90-day time-series momentum, else cash", "crypto", 4)
def _(d):
    b = d["X"]["BTC"]; return _xone(d, "BTC", (b / b.shift(90) - 1 > 0).astype(float))


# ============================================================ batch 5 (registered 2026-11-14 06:20 UTC, before running): filters & combos
def _mkt_trend(d):
    r = d["C"].pct_change(fill_method=None).where(d["ok"].shift(1, fill_value=False)).mean(axis=1).fillna(0)
    eq = (1 + r).cumprod()
    return eq > eq.rolling(200, min_periods=150).mean()

@strat("XS momentum 12-1 with crash filter (cash when market < 200d avg)", "stocks", 5)
def _(d):
    w = topk_monthly(d["C"].shift(21) / d["C"].shift(252) - 1, d["ok"])
    return w.mul(_mkt_trend(d).astype(float), axis=0)

@strat("Momentum acceleration (6m minus prior 6m, top 10%)", "stocks", 5)
def _(d):
    a = (d["C"] / d["C"].shift(126) - 1) - (d["C"].shift(126) / d["C"].shift(252) - 1)
    return topk_monthly(a, d["ok"])

@strat("Lowest 1-year max drawdown (top 10%)", "stocks", 5)
def _(d):
    c = d["C"]; dd = (c / c.rolling(252, min_periods=200).max() - 1).rolling(252, min_periods=200).min()
    return topk_monthly(dd, d["ok"])

@strat("Fresh 52-week high on 1.5x volume (last 5 days), monthly", "stocks", 5)
def _(d):
    hit = (d["C"] >= d["C"].rolling(252, min_periods=200).max()) & (d["V"] >= 1.5 * d["V"].rolling(50, min_periods=30).mean())
    score = hit.astype(float).rolling(5, min_periods=1).max() * (d["C"] / d["C"].shift(63))
    return topk_monthly(score.where(score > 0), d["ok"], k=30, min_n=5)

@strat("Top-200 liquid equal weight, only when market > 200d avg", "stocks", 5)
def _(d):
    me = month_end_mask(d["C"].index); w = pd.DataFrame(np.nan, index=d["C"].index, columns=d["C"].columns)
    for t in d["C"].index[me]:
        liq = d["dv"].loc[t].where(d["ok"].loc[t]).dropna().nlargest(200).index
        v = pd.Series(0.0, index=d["C"].columns); v[liq] = 1 / max(len(liq), 1); w.loc[t] = v
    return w.ffill().fillna(0.0).mul(_mkt_trend(d).astype(float), axis=0)

@strat("Sector top-3 momentum only when SPY > 200d avg, else IEF", "etfs", 5)
def _(d):
    E = d["E"]; base = REG["Sector rotation (top 3 SPDR sectors by 3m return)"][2](d)
    up = (E["SPY"] > E["SPY"].rolling(200).mean()).astype(float)
    w = base.mul(up, axis=0); w["IEF"] = w["IEF"] + (1 - up); return w

@strat("QQQ/TLT 60/40, 15% vol target, max 1.5x", "etfs", 5)
def _(d):
    E = d["E"]; r = 0.6 * E["QQQ"].pct_change(fill_method=None) + 0.4 * E["TLT"].pct_change(fill_method=None)
    lev = (0.15 / (r.rolling(21).std() * np.sqrt(252))).clip(upper=1.5)
    w = pd.DataFrame(0.0, index=E.index, columns=E.columns); w["QQQ"], w["TLT"] = 0.6 * lev, 0.4 * lev; return w.fillna(0.0)

@strat("ETF short-term reversal (3 worst of 20 ETFs by 5d, weekly)", "etfs", 5)
def _(d):
    E = d["E"][[c for c in d["E"].columns if not c.startswith("^")]]
    w = topk_monthly(E / E.shift(5) - 1, E.notna() & E.shift(60).notna(), k=3, largest=False, every="W")
    return w.reindex(columns=d["E"].columns, fill_value=0.0)


# ============================================================ batch 6 (registered 2026-11-14 09:25 UTC, before running): macro timing
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"


def fomc_dates() -> list:
    """Final day of each scheduled FOMC meeting, 2014 -> now, from federalreserve.gov (raises if too few found)."""
    import re, requests
    s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (research)"
    out = set()
    html = s.get("https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm", timeout=60).text
    for year, block in re.findall(r"(\d{4}) FOMC Meetings(.*?)(?=\d{4} FOMC Meetings|$)", html, flags=re.S):
        for mon, days in re.findall(r'fomc-meeting__month[^>]*>\s*<strong>(%s)(?:/\w+)?</strong>.*?fomc-meeting__date[^>]*>\s*([\d\-]+)' % MONTHS, block, flags=re.S):
            out.add(pd.Timestamp(f"{mon} {days.split('-')[-1]} {year}"))
    for y in range(2014, 2021):
        h = s.get(f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm", timeout=60).text
        for mon, a, b in re.findall(r"(%s)\s+(\d{1,2})(?:-(\d{1,2}))?\s+Meeting" % MONTHS, h):
            out.add(pd.Timestamp(f"{mon} {b or a} {y}"))
    out = sorted(d for d in out if d.year >= 2014)
    if len(out) < 70:
        raise RuntimeError(f"only {len(out)} FOMC dates parsed")
    return out

@strat("Pre-FOMC drift: SPY only the day before and day of FOMC decisions", "etfs", 6)
def _(d):
    idx = d["E"].index; pos = pd.Series(0.0, index=idx)
    for a in fomc_dates():
        i = idx.searchsorted(a)
        if i < len(idx) and idx[i] == a:
            for j in (i - 3, i - 2):             # weight at t earns t+1 -> t+2: covers days A-1 and A
                if j >= 0: pos.iloc[j] = 1.0
    return one(d, "SPY", pos)

@strat("Copper/gold momentum: SPY when copper beats gold over 3m, else IEF", "etfs", 6)
def _(d):
    E = d["E"]; ratio = E["HG=F"] / E["GC=F"]; up = (ratio / ratio.shift(63) - 1 > 0).astype(float)
    w = one(d, "SPY", up); w["IEF"] = 1 - up; return w

@strat("Gold trend: GLD above 200d avg, else BIL", "etfs", 6)
def _(d):
    g = d["E"]["GLD"]; up = (g > g.rolling(200).mean()).astype(float); w = one(d, "GLD", up); w["BIL"] = 1 - up; return w

@strat("Commodity trend: DBC above 200d avg, else BIL", "etfs", 6)
def _(d):
    g = d["E"]["DBC"]; up = (g > g.rolling(200).mean()).astype(float); w = one(d, "DBC", up); w["BIL"] = 1 - up; return w

@strat("Global relative strength: best of SPY/EFA/EEM by 6m, monthly", "etfs", 6)
def _(d):
    E = d["E"]; m = E[["SPY", "EFA", "EEM"]] / E[["SPY", "EFA", "EEM"]].shift(126) - 1; me = month_end_mask(E.index)
    w = pd.DataFrame(np.nan, index=E.index, columns=E.columns)
    for t in E.index[me]:
        if m.loc[t].isna().any(): continue
        v = pd.Series(0.0, index=E.columns); v[m.loc[t].idxmax()] = 1.0; w.loc[t] = v
    return w.ffill().fillna(0.0)


# ============================================================ batch 7 (registered 2026-11-14 12:20 UTC, before running):
# Reddit r/LETFs staples (synthetic daily-rebalanced leverage, 6%/yr on the borrowed part) and refined momentum.
@strat("Reddit LETF: 3x QQQ when QQQ > 200d avg, else cash (TQQQ-200SMA)", "etfs", 7)
def _(d):
    q = d["E"]["QQQ"]; return one(d, "QQQ", 3.0 * (q > q.rolling(200).mean()).astype(float))

@strat("Reddit LETF: HFEA 55% 3x SPY + 45% 3x TLT, quarterly rebalance", "etfs", 7)
def _(d):
    E = d["E"]; qe = pd.Series(E.index, index=E.index).groupby([E.index.year, E.index.quarter]).transform("max") == pd.Series(E.index, index=E.index)
    w = pd.DataFrame(np.nan, index=E.index, columns=E.columns)
    for t in E.index[qe]:
        v = pd.Series(0.0, index=E.columns); v["SPY"], v["TLT"] = 1.65, 1.35; w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Reddit LETF: 3x SPY when SPY > 200d avg, else cash", "etfs", 7)
def _(d):
    s = d["E"]["SPY"]; return one(d, "SPY", 3.0 * (s > s.rolling(200).mean()).astype(float))

@strat("Residual momentum (12-1 return minus market, top 10%)", "stocks", 7)
def _(d):
    r, m = _mret(d)
    res = r.sub(m, axis=0).fillna(0)
    score = res.rolling(231, min_periods=200).sum().shift(21)
    return topk_monthly(score, d["ok"])

@strat("Risk-adjusted momentum (12m Sharpe, top 10%)", "stocks", 7)
def _(d):
    r = d["C"].pct_change(fill_method=None)
    return topk_monthly(r.rolling(252, min_periods=200).mean() / r.rolling(252, min_periods=200).std(), d["ok"])

@strat("Momentum within the lower-beta half (12-1, top 10% of that half)", "stocks", 7)
def _(d):
    r, m = _mret(d)
    cov = (r.mul(m, axis=0)).rolling(60, min_periods=40).mean() - r.rolling(60, min_periods=40).mean().mul(m.rolling(60, min_periods=40).mean(), axis=0)
    beta = cov.div(m.rolling(60, min_periods=40).var(ddof=0), axis=0)
    low = beta.le(beta.where(d["ok"]).median(axis=1), axis=0)
    return topk_monthly(d["C"].shift(21) / d["C"].shift(252) - 1, d["ok"] & low, frac=0.2)


# ============================================================ batch 8 (registered 2026-11-14 15:20 UTC, before running): calendar & pullbacks
@strat("Santa Claus rally: SPY Dec 15 -> Jan 5 only", "etfs", 8)
def _(d):
    idx = d["E"].index
    on = pd.Series(((idx.month == 12) & (idx.day >= 15)) | ((idx.month == 1) & (idx.day <= 5)), index=idx).astype(float)
    return one(d, "SPY", on.shift(-2).fillna(0.0))

@strat("January effect: least-liquid decile in January only, else cash", "stocks", 8)
def _(d):
    w = topk_monthly(d["dv"], d["ok"], largest=False)
    jan = pd.Series(d["C"].index.month == 1, index=d["C"].index).astype(float).shift(-2).fillna(0.0)
    return w.mul(jan, axis=0)

@strat("Gap-and-go: gap up >= 2%, close > open, hold 10 days", "stocks", 8)
def _(d):
    sig = (d["O"] / d["C"].shift(1) - 1 >= 0.02) & (d["C"] > d["O"]) & d["ok"]
    act = sig.astype(float).rolling(10, min_periods=1).max()
    return act.div(act.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)

@strat("Pullback in leaders: top-20% 12-1 momentum with RSI(2) < 10, hold 5 days", "stocks", 8)
def _(d):
    c = d["C"]; dl = c.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 2).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 2).mean()
    rsi2 = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    mom = (c.shift(21) / c.shift(252) - 1).where(d["ok"]); lead = mom.ge(mom.quantile(0.8, axis=1), axis=0)
    sig = lead & (rsi2 < 10) & d["ok"]
    act = sig.astype(float).rolling(5, min_periods=1).max()
    return act.div(act.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
