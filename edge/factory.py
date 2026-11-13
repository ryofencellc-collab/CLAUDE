"""Strategy factory: a common engine, uniform pass rules, a growing ledger of every trial (PROTOCOL_FACTORY.md)."""
from __future__ import annotations
import math, os
import numpy as np, pandas as pd

from edge import stats as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "paper", "factory_ledger.csv")
REPORT = os.path.join(ROOT, "reports", "FACTORY.md")
COST = {"stocks": 0.001, "etfs": 0.001, "crypto": 0.0025}
BORROW = 0.06
SPLIT = pd.Timestamp("2022-01-01")
DEV0 = {"stocks": pd.Timestamp("2015-01-01"), "etfs": pd.Timestamp("2015-01-01"), "crypto": pd.Timestamp("2018-01-01")}


def returns(weights: pd.DataFrame, close: pd.DataFrame, market: str) -> pd.Series:
    """Daily strategy returns: weight set at t's close, traded at t+1's close, earns t+1 -> t+2."""
    w = weights.reindex(index=close.index, columns=close.columns).fillna(0.0)
    held = w.shift(1).fillna(0.0)                           # position traded at t+1 close
    r = close.pct_change(fill_method=None).fillna(0.0)
    gross = (held.shift(1).fillna(0.0) * r).sum(axis=1)     # earns from t+1 close to t+2 close
    turn = held.diff().abs().sum(axis=1).fillna(held.abs().sum(axis=1))
    lev = (held.shift(1).abs().sum(axis=1) - 1).clip(lower=0)
    return gross - turn * COST[market] - lev * BORROW / 252


def metrics(r: pd.Series, a, b) -> dict:
    x = r[(r.index >= a) & (r.index < b)]
    if len(x) < 60 or x.std() == 0:
        return dict(cagr=np.nan, sharpe=np.nan, dd=np.nan)
    eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    return dict(cagr=eq.iloc[-1] ** (1 / yrs) - 1, sharpe=x.mean() / x.std() * math.sqrt(252), dd=(eq / eq.cummax() - 1).min())


def evaluate(name: str, market: str, r: pd.Series, bench: pd.Series, end: pd.Timestamp) -> dict:
    d, h = metrics(r, DEV0[market], SPLIT), metrics(r, SPLIT, end)
    bh = metrics(bench, SPLIT, end)
    return dict(name=name, market=market, dev_cagr=d["cagr"], dev_sharpe=d["sharpe"], hold_cagr=h["cagr"], hold_sharpe=h["sharpe"],
                hold_dd=h["dd"], bench_cagr=bh["cagr"], bench_sharpe=bh["sharpe"],
                full_sr_daily=(r[r.index >= DEV0[market]].mean() / r[r.index >= DEV0[market]].std()) if r.std() > 0 else np.nan)


def judge(ledger: pd.DataFrame, rets: dict) -> pd.DataFrame:
    """Pass flags with the deflated Sharpe computed over every trial in the ledger."""
    n = len(ledger)
    var = float(np.nanvar(ledger["full_sr_daily"])) if n > 1 else 0.0
    out = ledger.copy()
    dsr = []
    for _, row in out.iterrows():
        r = rets.get(row["name"])
        dsr.append(S.deflated_sharpe(r[r.index >= DEV0[row["market"]]], n, var) if r is not None else row.get("dsr", np.nan))
    out["dsr"] = dsr
    out["PASS"] = ((out.hold_cagr >= 0.15) & (out.hold_sharpe >= 1.0) & (out.hold_sharpe > out.bench_sharpe) & (out.hold_dd >= -0.25)
                   & (out.dev_sharpe >= 0.5) & (out.dsr >= 0.95))
    return out


def report(led: pd.DataFrame) -> str:
    f = led.sort_values("hold_sharpe", ascending=False).copy()
    for c in ("dev_cagr", "hold_cagr", "hold_dd", "bench_cagr"):
        f[c] = f[c].map(lambda v: f"{v:.1%}" if pd.notna(v) else "")
    for c in ("dev_sharpe", "hold_sharpe", "bench_sharpe", "dsr"):
        f[c] = f[c].map(lambda v: f"{v:.2f}" if pd.notna(v) else "")
    f["PASS"] = f["PASS"].map(lambda v: "**YES**" if v else "")
    cols = ["name", "market", "batch", "dev_cagr", "dev_sharpe", "hold_cagr", "hold_sharpe", "hold_dd", "bench_cagr", "bench_sharpe", "dsr", "PASS"]
    return "\n".join([
        "# Strategy factory leaderboard", "",
        f"Rules: [PROTOCOL_FACTORY.md](../PROTOCOL_FACTORY.md). Trials so far: **{len(led)}**. Passing: **{int(led['PASS'].sum())}**. "
        "Holdout = 2022 → today. ROI as CAGR; bench = SPY (ETFs), equal-weight universe (stocks) or BTC (crypto).", "",
        f[[c for c in cols if c in f.columns]].to_markdown(index=False)]) + "\n"
