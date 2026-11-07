"""Round 30 (PROTOCOL_ROUND30.md): chart indicators vs Kalshi 15-minute BTC/ETH markets, beyond the price."""
import math
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("reports/ROUND30.md")
COINS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}
DEV_END, HOLD_END = pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
DECISIONS = (3, 5, 8, 10)
EDGE, SPREAD, STAKE = 0.0275, 0.01, 10.0
FEATS = ["rsi2", "rsi7", "st_dir", "ema_gap", "mom3", "mom5", "pos_in_range"]


def rsi(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    up, dn = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(), (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def supertrend_dir(c: pd.Series, n: int = 7, mult: float = 2.0) -> pd.Series:
    atr = c.diff().abs().ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    v = c.to_numpy()
    upper, lower = v + mult * atr, v - mult * atr
    d = np.ones(len(v))
    fu, fl = upper.copy(), lower.copy()
    for i in range(1, len(v)):
        fu[i] = min(upper[i], fu[i - 1]) if v[i - 1] <= fu[i - 1] else upper[i]
        fl[i] = max(lower[i], fl[i - 1]) if v[i - 1] >= fl[i - 1] else lower[i]
        d[i] = 1 if v[i] > fu[i - 1] else (-1 if v[i] < fl[i - 1] else d[i - 1])
    return pd.Series(d, index=c.index)


def samples(c: pd.Series) -> pd.DataFrame:
    """One row per (15-minute window, decision minute). c: 1-minute closes indexed by minute close time."""
    c = c[~c.index.duplicated()].asfreq("1min").ffill()
    lr = np.log(c).diff()
    sig = lr.rolling(60, min_periods=40).std()
    f = pd.DataFrame({"c": c, "sig": sig, "rsi2": rsi(c, 2), "rsi7": rsi(c, 7), "st_dir": supertrend_dir(c),
                      "ema_gap": (c.ewm(span=9).mean() - c.ewm(span=21).mean()) / c, "mom3": np.log(c).diff(3),
                      "mom5": np.log(c).diff(5)})
    start = c.index[(c.index.minute % 15) == 0]
    rows = []
    strike = c.reindex(start)
    end = c.reindex(start + pd.Timedelta(minutes=15))
    for m in DECISIONS:
        t = start + pd.Timedelta(minutes=m)
        g = f.reindex(t)
        hi = pd.concat([c.shift(k) for k in range(m + 1)], axis=1).max(axis=1).reindex(t).to_numpy()
        lo = pd.concat([c.shift(k) for k in range(m + 1)], axis=1).min(axis=1).reindex(t).to_numpy()
        tau = 15 - m
        d = pd.DataFrame({"t": t, "minute": m, "z": np.log(g["c"].to_numpy() / strike.to_numpy()) / (g["sig"].to_numpy() * math.sqrt(tau)),
                          "up": (end.to_numpy() >= strike.to_numpy()).astype(float)})
        for k in ["rsi2", "rsi7", "st_dir", "ema_gap", "mom3", "mom5"]:
            d[k] = g[k].to_numpy()
        d["pos_in_range"] = (g["c"].to_numpy() - lo) / np.where(hi - lo > 0, hi - lo, np.nan)
        d.loc[np.isnan(end.to_numpy()), "up"] = np.nan
        rows.append(d)
    out = pd.concat(rows, ignore_index=True).replace([np.inf, -np.inf], np.nan).dropna()
    out["rsi2"], out["rsi7"] = out["rsi2"] / 100 - 0.5, out["rsi7"] / 100 - 0.5
    return out


def fee(p: np.ndarray) -> np.ndarray:
    return np.ceil(0.07 * p * (1 - p) * 100 - 1e-9) / 100


def evaluate(df: pd.DataFrame) -> dict:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss
    dev, hold = df[df["t"] < DEV_END], df[(df["t"] >= DEV_END) & (df["t"] < HOLD_END)]
    xa = lambda d: np.column_stack([d["z"], d["z"] ** 3 / 10, d["minute"]])
    xb = lambda d: np.column_stack([xa(d), d[FEATS].to_numpy()])
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    A = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(xa(dev), dev["up"])
    B = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(xb(dev), dev["up"])
    pa, pb = A.predict_proba(xa(hold))[:, 1], B.predict_proba(xb(hold))[:, 1]
    y = hold["up"].to_numpy()
    res = {"n_dev": len(dev), "n_hold": len(hold), "ll_A": log_loss(y, pa), "ll_B": log_loss(y, pb),
           "acc_A": float(((pa > 0.5) == y).mean()), "acc_B": float(((pb > 0.5) == y).mean())}
    # betting: price = A's fair value (the market), buy B's side when the gap beats costs
    buy_up = pb - pa > EDGE
    buy_dn = pa - pb > EDGE
    price = np.where(buy_up, np.clip(pa + SPREAD / 2, 0.01, 0.99), np.clip(1 - pa + SPREAD / 2, 0.01, 0.99))
    win = np.where(buy_up, y == 1, y == 0)
    take = buy_up | buy_dn
    n = STAKE / price
    pnl = np.where(take, n * (win.astype(float) - price) - n * fee(price), 0.0)
    days = (HOLD_END - DEV_END).days
    res.update(bets=int(take.sum()), win_rate=float(win[take].mean()) if take.any() else float("nan"),
               pnl=float(pnl.sum()), per_day=float(pnl.sum() / days), per_bet=float(pnl[take].mean()) if take.any() else 0.0)
    # same, ignoring fees and spread: is there any raw signal at all?
    raw = np.where(take, STAKE / np.where(buy_up, pa, 1 - pa) * (win.astype(float) - np.where(buy_up, pa, 1 - pa)), 0.0)
    res["pnl_no_costs"] = float(raw.sum())
    coef = {k: float(v) for k, v in zip(["z", "z3", "minute"] + FEATS, np.round(B[-1].coef_[0], 3))}
    res["coef_B"] = coef
    return res


def main():
    from edge import round21
    lines = ["# Round 30: do chart indicators predict Kalshi 15-minute crypto markets beyond the price?", "",
             "Rules: [PROTOCOL_ROUND30.md](../PROTOCOL_ROUND30.md). Fit 2024–2025, judged on 2026-01..10.", ""]
    for name, sym in COINS.items():
        m = round21.minutes(sym, pd.Timestamp("2023-12-25", tz="UTC"), HOLD_END)
        print(name, len(m), flush=True)
        df = samples(m)
        df = df[df["t"] >= pd.Timestamp("2024-01-01", tz="UTC")]
        r = evaluate(df)
        print(name, r, flush=True)
        better = r["ll_B"] < r["ll_A"] - 0.0005
        lines += [f"## {name}", "",
                  f"Samples: dev {r['n_dev']:,}, holdout {r['n_hold']:,}.", "",
                  "| | price only (A) | price + indicators (B) |", "|---|---:|---:|",
                  f"| holdout log-loss (lower = better) | {r['ll_A']:.5f} | {r['ll_B']:.5f} |",
                  f"| holdout accuracy | {r['acc_A']:.2%} | {r['acc_B']:.2%} |", "",
                  f"Betting where B disagrees with the price by > {EDGE*100:.2f}c, $10 a bet, 2026: **{r['bets']:,} bets, "
                  f"win rate {r['win_rate']:.1%}, P&L ${r['pnl']:,.2f} (${r['per_day']:,.2f}/day)**; "
                  f"before fees and spread ${r['pnl_no_costs']:,.2f}.", "",
                  f"Indicators {'improve' if better else 'do not meaningfully improve'} on the price alone "
                  f"(log-loss gain {r['ll_A'] - r['ll_B']:+.5f}; > 0.0005 counts). "
                  f"Model B weights: {r['coef_B']}", ""]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
