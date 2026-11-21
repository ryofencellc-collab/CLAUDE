"""Round 72 (PROTOCOL_ROUND72.md): high-win-rate SPY put credit spreads, daily or Mon/Wed/Fri.  Usage: sample | report"""
import math, sys
from pathlib import Path
import numpy as np, pandas as pd
from edge import optbt as B

D = Path("data/opt")
DEV = (pd.Timestamp("2020-03-01"), pd.Timestamp("2024-01-01"))
HOLD = (pd.Timestamp("2024-01-01"), pd.Timestamp("2026-12-01"))
CAP0 = 25_000.0
DTES = {"short 7-21d": (7, 21, 14), "std 25-50d": (25, 50, 35)}


def slots(freq, dte):
    hold_td = dte[2] * 5 / 7
    return max(1, round(hold_td / (1 if freq == "daily" else 5 / 3)))


def configs():
    out = []
    for freq in ("daily", "mwf"):
        for dl in (0.10, 0.16, 0.25):
            for dn, dte in DTES.items():
                for manage in (False, True):
                    for cap in (0.30, 0.50, 0.70):
                        name = f"{freq} d{dl} {dn} {'managed' if manage else 'hold'} cap{int(cap * 100)}"
                        out.append(B.Strat(name, "put_spread", delta=dl, filt=("trend",), risk=cap / slots(freq, dte), manage=manage, freq=freq, dte=dte, cap=cap))
    return out


def load():
    chain = pd.read_pickle(D / "SPY.pkl"); px = pd.read_pickle(D / "SPY_px.pkl")["Close"]
    px.index = pd.to_datetime(px.index).tz_localize(None)
    book = B.Book(chain, px)
    print("SPY days", len(book.days), book.days[0].date(), book.days[-1].date(), flush=True)
    return {"SPY": book}, {"SPY": B.context(book)}, px


def bench(px, a, b):
    p = px[(px.index >= a) & (px.index < b)]
    r = p.pct_change().dropna(); yrs = (p.index[-1] - p.index[0]).days / 365.25
    return dict(cagr=(p.iloc[-1] / p.iloc[0]) ** (1 / yrs) - 1, sharpe=float(r.mean() / r.std() * math.sqrt(252)), max_dd=float((p / p.cummax() - 1).min()))


def one(st, books, ctxs, period):
    curve, trades = B.run([st], books, ctxs, {}, *period, capital=CAP0, budget={st.name: 1.0})
    s = B.stats(curve, trades, CAP0)
    s["trades_per_wk"] = len(trades) / max((period[1] - period[0]).days / 7, 1) if len(trades) else 0
    s["worst_trade"] = float(trades.pnl.min()) if len(trades) else np.nan
    s["avg_win"] = float(trades.pnl[trades.pnl > 0].mean()) if len(trades) and (trades.pnl > 0).any() else np.nan
    s["avg_loss"] = float(trades.pnl[trades.pnl <= 0].mean()) if len(trades) and (trades.pnl <= 0).any() else np.nan
    return s


def sample():
    books, ctxs, px = load()
    st = [c for c in configs() if c.name == "mwf d0.16 std 25-50d hold cap30"][0]
    b, c = books["SPY"], ctxs["SPY"]
    days = [d for d in b.days if pd.Timestamp("2023-01-01") <= d < pd.Timestamp("2023-07-01")]
    print("days in window", len(days), "weekday counts", pd.Series([d.weekday() for d in days]).value_counts().sort_index().to_dict())
    n_tr = sum(1 for d in days if b.spot(d) > c["sma200"].get(d, np.nan)); print("days above 200-day", n_tr)
    for d in days[:12]:
        e = B.entries(st, b, d, c)
        t = b.by_day[d]; exps = sorted({(x - d).days for x in t.expiration.unique()})
        print(d.date(), "dte available", exps[:8], "cands", [(round(oc, 2), round(ml, 0)) for _, oc, ml, *_ in e])
    s = one(st, books, ctxs, (pd.Timestamp("2023-01-01"), pd.Timestamp("2023-07-01")))
    print("SAMPLE", st.name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()})


def fmt(s):
    return dict(cagr=round(100 * s["cagr"], 1), sharpe=round(s["sharpe"], 2), max_dd=round(100 * s["max_dd"], 1), win=round(100 * s["win_rate"], 1) if s["win_rate"] == s["win_rate"] else np.nan,
                trades=s["trades"], per_wk=round(s["trades_per_wk"], 1), avg_win=round(s["avg_win"], 0) if s["avg_win"] == s["avg_win"] else np.nan,
                avg_loss=round(s["avg_loss"], 0) if s["avg_loss"] == s["avg_loss"] else np.nan, worst=round(s["worst_trade"], 0) if s["worst_trade"] == s["worst_trade"] else np.nan, final=round(s["final"], 0))


def report():
    books, ctxs, px = load()
    rows = []
    for i, st in enumerate(configs()):
        dv, ho = one(st, books, ctxs, DEV), one(st, books, ctxs, HOLD)
        rows.append(dict(config=st.name, **{f"dev_{k}": v for k, v in fmt(dv).items()}, **{f"ho_{k}": v for k, v in fmt(ho).items()}))
        if i % 6 == 0: print(i, st.name, rows[-1]["dev_cagr"], rows[-1]["ho_cagr"], flush=True)
    R = pd.DataFrame(rows)
    bd, bh = bench(px, *DEV), bench(px, *HOLD)
    elig = R[(R.dev_win >= 85) & (R.dev_cagr >= 8)]
    pick = elig.sort_values("dev_sharpe", ascending=False).iloc[0] if len(elig) else None
    passed = bool(pick is not None and pick.ho_win >= 85 and pick.ho_cagr >= 12 and pick.ho_sharpe >= bh["sharpe"] and pick.ho_max_dd > 100 * bh["max_dd"])
    b = lambda x: f"CAGR {100 * x['cagr']:.1f}%, Sharpe {x['sharpe']:.2f}, max drop {100 * x['max_dd']:.1f}%"
    out = ["# Round 72: SPY put credit spreads, daily or 3× a week, real option prices", "", "Rules: [PROTOCOL_ROUND72.md](../PROTOCOL_ROUND72.md). $25,000 account, natural fills, $0.65/contract/leg, opened only above the 200-day average.", "",
           f"SPY buy-and-hold: dev {b(bd)}; holdout {b(bh)}.", ""]
    if pick is not None:
        out += [f"**Dev choice:** {pick.config}. Holdout: CAGR {pick.ho_cagr}%, Sharpe {pick.ho_sharpe}, max drop {pick.ho_max_dd}%, win rate {pick.ho_win}%, {pick.ho_per_wk} trades/week.", ""]
    out += [f"**Verdict: {'PASS → live paper tracker' if passed else 'FAIL'}.**", "",
            "## All 72 configurations (dev 2020-03 → 2023, holdout 2024 → 2026-11)", "", R.sort_values("dev_sharpe", ascending=False).to_markdown(index=False), ""]
    open("reports/ROUND72.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:12]))
    R.to_csv("data/r72_grid.csv", index=False)


if __name__ == "__main__":
    {"sample": sample, "report": report}[sys.argv[1]]()
