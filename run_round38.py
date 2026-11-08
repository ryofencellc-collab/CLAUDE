"""Round 38 (PROTOCOL_ROUND38.md): simple swing strategies (breakouts, dip-buys), <=3 trades/week, daily OHLC.
python run_round38.py data   -> data/r38/{stocks,etfs,crypto}_{O,H,L,C,V}.pkl
python run_round38.py run    -> reports/ROUND38.md"""
import io
import math
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import requests

D, OUT = Path("data/r38"), Path("reports/ROUND38.md")
COST = 0.0010
ETFS = ["SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLB", "XLU", "XLRE", "XLC"]
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK", "DOT", "LTC", "TRX", "MATIC", "POL", "ATOM", "NEAR",
         "UNI", "ETC", "FIL", "APT", "ARB", "OP", "INJ", "SUI", "AAVE", "BCH", "XLM", "HBAR", "ICP", "RNDR", "RENDER", "TON"]
SPLITS = {"stocks": ("2015-01-01", "2022-01-01", "2026-12-01"), "etfs": ("2015-01-01", "2022-01-01", "2026-12-01"),
          "crypto": ("2019-01-01", "2023-01-01", "2026-11-01")}


# ------------------------------------------------------------------ data
def yahoo(tickers, name):
    import yfinance as yf
    panels = {k: [] for k in ("Open", "High", "Low", "Close", "Volume")}
    for i in range(0, len(tickers), 200):
        chunk = tickers[i:i + 200]
        for _ in range(3):
            try:
                df = yf.download(chunk, start="2014-01-01", auto_adjust=True, progress=False, group_by="column", threads=True)
                break
            except Exception as e:
                print("retry", e, flush=True)
        else:
            continue
        for k in panels:
            if k in df:
                x = df[k]
                if isinstance(x, pd.Series):
                    x = x.to_frame(chunk[0])
                panels[k].append(x.astype("float32"))
        print(name, i + len(chunk), "/", len(tickers), flush=True)
    for k, parts in panels.items():
        p = pd.concat(parts, axis=1)
        p = p.loc[:, ~p.columns.duplicated()].dropna(axis=1, how="all")
        p.to_pickle(D / f"{name}_{k[0]}.pkl")


def binance(sym):
    parts = []
    for m in pd.period_range("2018-01", "2026-10", freq="M"):
        try:
            r = requests.get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1d/{sym}-1d-{m}.zip", timeout=30)
        except requests.RequestException:
            continue
        if r.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                parts.append(pd.read_csv(z.open(z.namelist()[0]), header=None))
    if not parts:
        return None
    df = pd.concat(parts)
    t = pd.to_numeric(df[0]).to_numpy()
    t = np.where(t > 1e14, t // 1000, t)
    out = pd.DataFrame({"O": df[1].astype(float).values, "H": df[2].astype(float).values, "L": df[3].astype(float).values,
                        "C": df[4].astype(float).values, "V": df[7].astype(float).values},
                       index=pd.to_datetime(t, unit="ms").normalize())
    return out[~out.index.duplicated()].sort_index()


def data():
    import run_round36 as R36
    D.mkdir(parents=True, exist_ok=True)
    yahoo(ETFS, "etfs")
    with ThreadPoolExecutor(8) as ex:
        got = dict(zip(COINS, ex.map(lambda c: binance(f"{c}USDT"), COINS)))
    got = {c: f for c, f in got.items() if f is not None and len(f) > 200}
    for k in "OHLCV":
        pd.DataFrame({c: f[k] for c, f in got.items()}).sort_index().to_pickle(D / f"crypto_{k}.pkl")
    print("crypto", list(got), flush=True)
    yahoo(R36.universe(), "stocks")


# ------------------------------------------------------------------ strategies
@dataclass
class Spec:
    name: str
    kind: str          # "breakout" | "dip"
    n: int = 20        # breakout lookback
    exit: str = "2R"   # "1R" | "2R" | "trail" | "ma5" | "upclose" | "abovehigh" | "sameday"
    squeeze: bool = False
    dip: str = ""      # "rsi10" | "rsi5" | "3down" | "ibs" | "gapdown"


SPECS = []
for n in (20, 55):
    for ex in ("1R", "2R", "trail"):
        SPECS.append(Spec(f"B{1 if n == 20 else 2} breakout {n}d, exit {ex}", "breakout", n, ex))
for ex in ("2R", "trail"):
    SPECS.append(Spec(f"B3 squeeze breakout, exit {ex}", "breakout", 20, ex, squeeze=True))
SPECS += [Spec("D1 RSI(2)<10 in uptrend", "dip", exit="ma5", dip="rsi10"), Spec("D2 RSI(2)<5 in uptrend", "dip", exit="ma5", dip="rsi5"),
          Spec("D3 3 down closes in uptrend", "dip", exit="upclose", dip="3down"), Spec("D4 IBS<0.2 in uptrend", "dip", exit="abovehigh", dip="ibs"),
          Spec("D5 gap down >=2% in uptrend, open->close", "dip", exit="sameday", dip="gapdown")]


def rsi(c, n):
    d = c.diff()
    up, dn = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(), (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def features(O, H, L, C, V, market):
    f = {"O": O, "H": H, "L": L, "C": C}
    tr = pd.concat([H - L, (H - C.shift()).abs(), (L - C.shift()).abs()]).groupby(level=0).max()
    f["atr"] = tr.reindex(C.index).rolling(14, min_periods=10).mean()
    dv = (C * V).rolling(20, min_periods=15).mean()
    f["ok"] = ((C >= 10) & (dv >= 20e6)) if market == "stocks" else (dv >= 1e6) if market == "etfs" else (dv >= 5e6)
    f["vr"] = V / V.rolling(50, min_periods=30).mean().shift(1)
    f["hi20"], f["hi55"] = H.rolling(20).max().shift(1), H.rolling(55).max().shift(1)
    f["lo10"] = L.rolling(10).min().shift(1)
    f["sma200"], f["sma5"] = C.rolling(200, min_periods=150).mean(), C.rolling(5).mean()
    sd = C.rolling(20).std()
    bw = 4 * sd / C.rolling(20).mean()
    f["sq"] = bw <= bw.rolling(120, min_periods=80).quantile(0.10)
    f["rsi2"] = rsi(C, 2)
    f["down3"] = (C < C.shift(1)) & (C.shift(1) < C.shift(2)) & (C.shift(2) < C.shift(3))
    rng = (H - L).replace(0, np.nan)
    f["ibs"] = (C - L) / rng
    return f


def signals(sp: Spec, f):
    up = f["C"] > f["sma200"]
    if sp.kind == "breakout":
        lvl = f["hi20"] if sp.n == 20 else f["hi55"]
        s = (f["C"] > lvl) & (f["vr"] >= 1.5) & f["ok"]
        if sp.squeeze:
            s &= f["sq"].shift(1).fillna(False)
        return s.fillna(False), f["vr"]
    if sp.dip == "rsi10":
        return (up & (f["rsi2"] < 10) & f["ok"]).fillna(False), -f["rsi2"]
    if sp.dip == "rsi5":
        return (up & (f["rsi2"] < 5) & f["ok"]).fillna(False), -f["rsi2"]
    if sp.dip == "3down":
        return (up & f["down3"] & f["ok"]).fillna(False), -(f["C"] / f["C"].shift(3) - 1)
    if sp.dip == "ibs":
        return (up & (f["ibs"] < 0.2) & f["ok"]).fillna(False), -f["ibs"]
    if sp.dip == "gapdown":   # known at the open of day t: uptrend and liquidity as of t-1
        gap = f["O"] / f["C"].shift(1) - 1
        s = (gap <= -0.02) & up.shift(1).fillna(False) & f["ok"].shift(1).fillna(False)
        return s.fillna(False), -gap
    raise ValueError(sp)


def simulate(sp: Spec, f, start, end, risk=0.02, capital=25_000.0, max_week=3, slots=5):
    O, H, L, C = (f[k].to_numpy(dtype=float) for k in "OHLC")
    atr = f["atr"].to_numpy(dtype=float)
    lo10, sma5 = f["lo10"].to_numpy(dtype=float), f["sma5"].to_numpy(dtype=float)
    sig, rank = signals(sp, f)
    sig = sig.to_numpy() & ((f["C"].index >= start) & (f["C"].index < end))[:, None]
    rk = np.nan_to_num(rank.to_numpy(dtype=float), nan=-1e9)
    dates = f["C"].index
    n = len(dates)
    week = dates.isocalendar().week.to_numpy() + 100 * dates.isocalendar().year.to_numpy()
    cash, pos, trades, curve = capital, [], [], np.full(n, np.nan)
    pending = []                     # (col, stop_mult) to enter at the next open
    used = {}
    same_day = sp.exit == "sameday"
    for i in range(n):
        if not (dates[i] >= start and dates[i] < end) and not pos and not pending:
            continue
        eq_open = cash + sum(p["sh"] * (C[i - 1, p["col"]] if i else p["entry"]) for p in pos)
        # entries at today's open (signals from yesterday's close, or today's gap-down)
        if same_day and dates[i] >= start and dates[i] < end:
            cand = np.where(sig[i])[0]
            pending = [c for c in cand[np.argsort(-rk[i, cand])]]
        for col in pending:
            if len(pos) >= slots or used.get(week[i], 0) >= max_week:
                break
            if any(p["col"] == col for p in pos):
                continue
            px = O[i, col]
            if not (np.isfinite(px) and px > 0):
                continue
            entry = px * (1 + COST)
            if sp.kind == "breakout":
                a = atr[i - 1, col] if i else np.nan
                if not (np.isfinite(a) and a > 0):
                    continue
                stop = px - 1.5 * a
                rps = entry - stop
                sh = risk * eq_open / rps
                tgt = entry + (1 if sp.exit == "1R" else 2) * rps if sp.exit in ("1R", "2R") else np.inf
            else:
                stop, rps, tgt = -np.inf, np.nan, np.inf
                sh = 0.20 * eq_open / entry
            gross = sum(p["sh"] * O[i, p["col"]] for p in pos if np.isfinite(O[i, p["col"]]))
            sh = min(sh, max(0.0, eq_open - gross) / entry)
            if sh * entry < 50:
                continue
            cash -= sh * entry
            pos.append({"col": col, "sh": sh, "entry": entry, "stop": stop, "tgt": tgt, "rps": rps, "e": i})
            used[week[i]] = used.get(week[i], 0) + 1
        pending = []
        # exits during / at the end of day i
        keep = []
        for p in pos:
            c = p["col"]
            o, h, l, cl = O[i, c], H[i, c], L[i, c], C[i, c]
            px = None
            if not np.isfinite(cl):
                keep.append(p)
                continue
            if np.isfinite(p["stop"]):
                if i > p["e"] and o <= p["stop"]:
                    px = o
                elif l <= p["stop"]:
                    px = p["stop"]
            if px is None and np.isfinite(p["tgt"]):
                if i > p["e"] and o >= p["tgt"]:
                    px = o
                elif h >= p["tgt"]:
                    px = p["tgt"]
            held = i - p["e"] + 1
            if px is None:
                if sp.exit == "sameday":
                    px = cl
                elif sp.exit == "trail" and np.isfinite(lo10[i, c]) and cl < lo10[i, c]:
                    px = cl
                elif sp.exit == "ma5" and (cl > sma5[i, c] or held >= 10):
                    px = cl
                elif sp.exit == "upclose" and ((i > 0 and cl > C[i - 1, c]) or held >= 5):
                    px = cl
                elif sp.exit == "abovehigh" and ((i > 0 and cl > H[i - 1, c]) or held >= 5):
                    px = cl
                elif sp.kind == "breakout" and held >= 20:
                    px = cl
            if px is None:
                keep.append(p)
                continue
            out = px * (1 - COST)
            cash += p["sh"] * out
            ret = out / p["entry"] - 1
            trades.append({"date": dates[i], "ret": ret, "R": (out - p["entry"]) / p["rps"] if np.isfinite(p["rps"]) else np.nan,
                           "days": held})
        pos = keep
        curve[i] = cash + sum(p["sh"] * C[i, p["col"]] for p in pos if np.isfinite(C[i, p["col"]]))
        # tomorrow's entries from today's close
        if not same_day and dates[i] >= start and dates[i] < end:
            cand = np.where(sig[i])[0]
            pending = list(cand[np.argsort(-rk[i, cand])])
    cv = pd.Series(curve, index=dates).dropna()
    return cv, pd.DataFrame(trades)


def stats(cv, tr, capital=25_000.0):
    if cv.empty:
        return {}
    if tr.empty:
        tr = pd.DataFrame({"ret": pd.Series(dtype=float)})
    r = cv.pct_change().dropna()
    yrs = max((cv.index[-1] - cv.index[0]).days / 365.25, 0.1)
    ann = (cv.iloc[-1] / capital) ** (1 / yrs) - 1 if cv.iloc[-1] > 0 else -1
    wk = max((cv.index[-1] - cv.index[0]).days / 7, 1)
    t = tr["ret"].mean() / (tr["ret"].std() / math.sqrt(len(tr))) if len(tr) > 2 and tr["ret"].std() > 0 else 0.0
    wins, losses = tr[tr["ret"] > 0], tr[tr["ret"] <= 0]
    return {"ann": ann, "sharpe": float(r.mean() / r.std() * math.sqrt(252)) if r.std() > 0 else 0.0,
            "maxdd": float((cv / cv.cummax() - 1).min()), "trades": len(tr), "per_week": len(tr) / wk,
            "win": float((tr["ret"] > 0).mean()) if len(tr) else np.nan, "avg_win": wins["ret"].mean() if len(wins) else 0,
            "avg_loss": losses["ret"].mean() if len(losses) else 0, "exp": tr["ret"].mean() if len(tr) else 0, "t": t,
            "per_day_25k": (cv.iloc[-1] - capital) / max((cv.index[-1] - cv.index[0]).days, 1)}


def run():
    lines = ["# Round 38: simple swing strategies (2–3 trades a week)", "",
             "Rules: [PROTOCOL_ROUND38.md](../PROTOCOL_ROUND38.md). Next-open entries, stop-before-target, 0.10% per side, ≤ 3 new trades/week, ≤ 5 open, "
             "risk 2% to the stop (breakouts) or 20% of equity per trade (dip-buys).", ""]
    allrows = []
    for market in ("etfs", "crypto", "stocks"):
        try:
            O, H, L, C, V = (pd.read_pickle(D / f"{market}_{k}.pkl").astype(float) for k in "OHLCV")
        except FileNotFoundError:
            lines += [f"## {market}: no data", ""]
            continue
        cols = C.columns
        O, H, L, V = (x.reindex(index=C.index, columns=cols) for x in (O, H, L, V))
        f = features(O, H, L, C, V, market)
        s0, split, s1 = (pd.Timestamp(x) for x in SPLITS[market])
        rows = []
        for sp in SPECS:
            dv_cv, dv_tr = simulate(sp, f, s0, split)
            ho_cv, ho_tr = simulate(sp, f, split, s1)
            dv, ho = stats(dv_cv, dv_tr), stats(ho_cv, ho_tr)
            if not ho or not dv:
                continue
            ok = dv["ann"] > 0 and ho["ann"] > 0 and ho["sharpe"] >= 1.0 and ho["t"] >= 3.0 and ho["per_week"] >= 1.0
            row = {"market": market, "strategy": sp.name, "dev %/yr": round(100 * dv["ann"], 1), "dev win %": round(100 * dv["win"], 0),
                   "hold %/yr": round(100 * ho["ann"], 1), "hold Sharpe": round(ho["sharpe"], 2), "hold worst drop": f"{ho['maxdd']:.0%}",
                   "trades/wk": round(ho["per_week"], 2), "win %": round(100 * ho["win"], 0),
                   "avg win": f"{ho['avg_win']:.1%}", "avg loss": f"{ho['avg_loss']:.1%}", "avg trade": f"{ho['exp']:.2%}",
                   "t": round(ho["t"], 2), "$25k/day": round(ho["per_day_25k"], 2), "PASS": "YES" if ok else ""}
            rows.append(row)
            allrows.append((row, sp, market, f, split, s1))
            print(row, flush=True)
        tab = pd.DataFrame(rows).sort_values("hold Sharpe", ascending=False)
        lines += [f"## {market.upper()} (dev {s0.date()}–{split.date()}, holdout {split.date()}–{s1.date()})", "", tab.drop(columns=["market"]).to_markdown(index=False), ""]
    passed = [x for x in allrows if x[0]["PASS"] == "YES"]
    best = passed or sorted(allrows, key=lambda x: -x[0]["hold Sharpe"])[:3]
    lines += ["## Risk per trade (holdout): what " + ("the passing strategies" if passed else "the best three (none passed)") + " make at 1%, 2%, 5%", ""]
    srows = []
    for row, sp, market, f, a, b in best:
        for rk in (0.01, 0.02, 0.05):
            for cap in (25_000.0, 1_000.0):
                cv, tr = simulate(sp, f, a, b, risk=rk, capital=cap)
                st = stats(cv, tr, cap)
                srows.append({"market": market, "strategy": sp.name, "risk": f"{rk:.0%}", "start": f"${cap:,.0f}",
                              "%/yr": round(100 * st["ann"], 1), "worst drop": f"{st['maxdd']:.0%}", "$/day": round(st["per_day_25k"], 2),
                              "end": f"${cv.iloc[-1]:,.0f}"})
    lines += [pd.DataFrame(srows).to_markdown(index=False)]
    n_pass = len(passed)
    lines.insert(4, f"**{n_pass} of {len(allrows)} configs pass.**\n")
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    {"data": data, "run": run}[sys.argv[1]]()
