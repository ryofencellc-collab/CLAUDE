"""Round 42 (PROTOCOL_ROUND42.md): diversified long-only trend following, ETFs + BTC/ETH/SOL."""
import math, os
import numpy as np, pandas as pd
from run_round38 import binance

ETFS = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "IEF", "GLD", "SLV", "DBC", "USO", "UUP", "VNQ"]
COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
DEV, HOLD, END = pd.Timestamp("2018-07-01"), pd.Timestamp("2023-01-01"), pd.Timestamp("2026-11-01")
C_ETF, C_CRY, BORROW = 0.0005, 0.0040, 0.08
D = "data/r42"


def etf_prices():
    p = f"{D}/etf.pkl"
    if os.path.exists(p): return pd.read_pickle(p)
    import yfinance as yf
    x = yf.download(ETFS, start="2006-01-01", auto_adjust=True, progress=False)["Close"]
    x.index = pd.to_datetime(x.index).tz_localize(None)
    os.makedirs(D, exist_ok=True); x.to_pickle(p); return x


def coin_prices():
    p = f"{D}/coins.pkl"
    if os.path.exists(p): return pd.read_pickle(p)
    x = pd.DataFrame({s[:-4]: binance(s)["C"] for s in COINS})
    os.makedirs(D, exist_ok=True); x.to_pickle(p); return x


def month_ends(idx):
    s = pd.Series(idx, index=idx)
    return set(s.groupby([idx.year, idx.month]).max())


def backtest(px, target, cost):
    """target: weights decided at close t, held from t+1 (traded at the close of t+1... approximated as next-day returns)."""
    r = px.pct_change().fillna(0.0)
    w = target.shift(1).fillna(0.0)          # one-day lag: decide at t's close, earn from t+1
    turn = w.diff().abs().sum(axis=1).fillna(w.abs().sum(axis=1))
    return (w * r).sum(axis=1) - turn * cost


def e1(px):
    me = month_ends(px.index); ret = px.pct_change(252); vol = px.pct_change().rolling(63).std()
    w = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
    for t in px.index:
        if t in me:
            on = (ret.loc[t] > 0) & vol.loc[t].notna()
            iv = (1 / vol.loc[t]).where(on, 0.0).fillna(0.0)
            w.loc[t] = iv / iv.sum() if iv.sum() > 0 else 0.0
    return w.ffill().fillna(0.0)


def e2(px):
    me = month_ends(px.index); sma = px.rolling(210).mean()
    w = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
    n = px.shape[1]
    for t in px.index:
        if t in me:
            w.loc[t] = ((px.loc[t] > sma.loc[t]) & sma.loc[t].notna()).astype(float) / n
    return w.ffill().fillna(0.0)


def c1(px):
    hi, lo = px.rolling(55).max().shift(1), px.rolling(20).min().shift(1)
    st = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
    st[px > hi] = 1.0; st[px < lo] = 0.0
    return st.ffill().fillna(0.0) / px.shape[1]


def c2(px):
    return ((px > px.rolling(100).mean()) & px.notna()).astype(float) / px.shape[1]


def stats(r, a, b):
    r = r[(r.index >= a) & (r.index < b)]
    if len(r) < 20: return dict(cagr=np.nan, sharpe=np.nan, maxdd=np.nan)
    eq = (1 + r).cumprod(); yrs = (r.index[-1] - r.index[0]).days / 365.25
    return dict(cagr=eq.iloc[-1] ** (1 / yrs) - 1, sharpe=r.mean() / r.std() * math.sqrt(252) if r.std() > 0 else 0,
                maxdd=(eq / eq.cummax() - 1).min())


def lever(r, k):
    return k * r - (k - 1) * BORROW / 252


def main():
    E, C = etf_prices(), coin_prices()
    idx = E.index  # trade on US trading days; crypto marked at the same dates
    C = C.reindex(idx, method="ffill")
    rules = {"E1 12m momentum": (E, e1(E), C_ETF), "E2 10m average": (E, e2(E), C_ETF),
             "C1 Donchian 55/20": (C, c1(C), C_CRY), "C2 100d average": (C, c2(C), C_CRY)}
    R = {k: backtest(px, w, c) for k, (px, w, c) in rules.items()}
    R["SPY buy-and-hold"] = E["SPY"].pct_change().fillna(0)
    R["BTC buy-and-hold"] = C["BTC"].pct_change().fillna(0)
    R["60/40 SPY/IEF"] = 0.6 * E["SPY"].pct_change().fillna(0) + 0.4 * E["IEF"].pct_change().fillna(0)
    rows = []
    for k, r in R.items():
        dv, ho, lg = stats(r, DEV, HOLD), stats(r, HOLD, END), stats(r, pd.Timestamp("2008-01-01"), END)
        rows.append({"rule": k, "dev CAGR": dv["cagr"], "dev Sharpe": dv["sharpe"], "hold CAGR": ho["cagr"],
                     "hold Sharpe": ho["sharpe"], "hold worst drop": ho["maxdd"], "2008+ CAGR": lg["cagr"] if k[0] == "E" or "SPY" in k or "60" in k else np.nan,
                     "2008+ Sharpe": lg["sharpe"] if k[0] == "E" or "SPY" in k or "60" in k else np.nan})
    T = pd.DataFrame(rows)
    pe = max(["E1 12m momentum", "E2 10m average"], key=lambda k: stats(R[k], DEV, HOLD)["sharpe"])
    pc = max(["C1 Donchian 55/20", "C2 100d average"], key=lambda k: stats(R[k], DEV, HOLD)["sharpe"])
    dv = lambda k: R[k][(R[k].index >= DEV) & (R[k].index < HOLD)].std()
    we = (1 / dv(pe)) / (1 / dv(pe) + 1 / dv(pc)); wc = 1 - we
    # monthly rebalance of the two sleeves back to (we, wc)
    me = month_ends(idx); ve, vc, P = we, wc, []
    for t in idx:
        g = ve * R[pe][t] + vc * R[pc][t]; tot = ve + vc
        ve, vc = ve * (1 + R[pe][t]), vc * (1 + R[pc][t])
        P.append(g / tot)
        if t in me:
            s = ve + vc; ve, vc = we * s, wc * s
    P = pd.Series(P, index=idx)
    out = ["# Round 42: diversified long-only trend following (ETFs + BTC/ETH/SOL)", "",
           f"Rules: [PROTOCOL_ROUND42.md](../PROTOCOL_ROUND42.md). Dev {DEV.date()} → {HOLD.date()}, holdout → {END.date()}.", ""]
    f = T.copy()
    for c in f.columns[1:]:
        f[c] = f[c].map(lambda v: "" if pd.isna(v) else (f"{v:.1%}" if "CAGR" in c or "drop" in c else f"{v:.2f}"))
    out += [f.to_markdown(index=False), "", f"**Portfolio:** {pe} ({we:.0%} of capital) + {pc} ({wc:.0%}), monthly rebalance.", ""]
    prow = []
    for k in (1.0, 1.5, 2.0):
        r = lever(P, k); d, h = stats(r, DEV, HOLD), stats(r, HOLD, END)
        yrs = (END - HOLD).days / 365.25
        prow.append({"leverage": f"{k}×", "dev CAGR": f"{d['cagr']:.1%}", "dev Sharpe": f"{d['sharpe']:.2f}",
                     "hold CAGR": f"{h['cagr']:.1%}", "hold Sharpe": f"{h['sharpe']:.2f}", "hold worst drop": f"{h['maxdd']:.1%}",
                     **{f"$/day on ${c // 1000}k": f"${c * h['cagr'] / 365:.2f}" for c in (1000, 10000, 25000)}})
    out += [pd.DataFrame(prow).to_markdown(index=False), ""]
    h1 = stats(P, HOLD, END); d1 = stats(P, DEV, HOLD)
    bh = max(stats(R["SPY buy-and-hold"], HOLD, END)["sharpe"], stats(R["BTC buy-and-hold"], HOLD, END)["sharpe"])
    ok = h1["sharpe"] >= 1 and h1["cagr"] >= 0.15 and h1["maxdd"] >= -0.25 and d1["cagr"] > 0 and h1["sharpe"] > bh
    out.append(f"**Pass (holdout 1×: Sharpe ≥ 1, CAGR ≥ 15%, worst drop ≥ −25%, dev > 0, beats buy-and-hold Sharpe {bh:.2f}):"
               f" {'PASS' if ok else 'FAIL'}.**")
    yr = pd.DataFrame({"portfolio": P, pe: R[pe], pc: R[pc], "SPY": R["SPY buy-and-hold"]})
    yr = yr[yr.index >= DEV].groupby(yr.index[yr.index >= DEV].year).apply(lambda x: (1 + x).prod() - 1)
    out += ["", "## By year", "", yr.map(lambda v: f"{v:.1%}").to_markdown()]
    open("reports/ROUND42.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    main()
