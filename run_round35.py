"""Round 35 runner (PROTOCOL_ROUND35.md): python run_round35.py  (expects data/opt/*.pkl from round35_data)."""
import math
from pathlib import Path

import numpy as np
import pandas as pd

from edge import optbt as B
from edge import stats as S

D = Path("data/opt")
OUT = Path("reports/ROUND35.md")
DEV = (pd.Timestamp("2020-03-01"), pd.Timestamp("2024-01-01"))
HOLD = (pd.Timestamp("2024-01-01"), pd.Timestamp("2026-12-01"))
STOCKS = ("AAPL", "MSFT", "NVDA", "AMZN", "META", "TSLA", "GOOGL")
CAP = 25_000.0

CONFIGS = [B.Strat(f"S1 put spread d{d} {'+'.join(f) or 'no filter'}", "put_spread", delta=d, filt=f)
           for d in (0.16, 0.30) for f in ((), ("trend",), ("ivr",), ("trend", "ivr"))]
CONFIGS += [B.Strat(f"S1h put spread d{d} {'+'.join(f) or 'no filter'} hold to expiry", "put_spread", delta=d, filt=f, manage=False)
            for d in (0.16, 0.30) for f in ((), ("trend",))]
CONFIGS += [B.Strat("S2 iron condor d0.16 no filter", "condor", delta=0.16),
            B.Strat("S2 iron condor d0.16 ivr", "condor", delta=0.16, filt=("ivr",)),
            B.Strat("S3 call spread d0.30 downtrend", "call_spread", delta=0.30, filt=("downtrend",)),
            B.Strat("S4 call debit spread on breakouts", "call_debit", filt=("breakout",)),
            B.Strat("S5 put debit spread on breakdowns", "put_debit", filt=("breakdown",)),
            B.Strat("S6a earnings iron fly", "earn_fly", risk=0.03, symbols=STOCKS),
            B.Strat("S6b earnings 16d iron condor", "earn_condor", risk=0.03, symbols=STOCKS),
            B.Strat("S6c earnings long straddle", "earn_straddle", risk=0.03, symbols=STOCKS),
            B.Strat("S7 put spread d0.30 VIX contango", "put_spread", delta=0.30, filt=("contango",))]


def load():
    books, ctxs, earn = {}, {}, {}
    vix = None
    try:
        import yfinance as yf
        v = yf.download(["^VIX", "^VIX3M"], start="2019-06-01", progress=False)["Close"]
        vix = pd.DataFrame({"VIX": v["^VIX"], "VIX3M": v["^VIX3M"]}).dropna()
    except Exception as e:
        print("VIX download failed:", e)
    for sym in ("SPY",) + STOCKS:
        p = D / f"{sym}.pkl"
        if not p.exists():
            print("missing", sym)
            continue
        chain = pd.read_pickle(p)
        px = pd.read_pickle(D / f"{sym}_px.pkl")["Close"]
        px.index = pd.to_datetime(px.index).tz_localize(None)
        books[sym] = B.Book(chain, px)
        ctxs[sym] = B.context(books[sym], vix if sym == "SPY" else None)
        ef = D / f"{sym}_earnings.txt"
        earn[sym] = [pd.Timestamp(x) for x in ef.read_text().split()] if ef.exists() else []
        print(f"{sym}: {len(books[sym].days)} days {books[sym].days[0].date() if books[sym].days else ''}..{books[sym].days[-1].date() if books[sym].days else ''}, "
              f"{len(earn[sym])} earnings dates", flush=True)
    return books, ctxs, earn


def evaluate(st_list, books, ctxs, earn, period, budget=None):
    curve, trades = B.run(st_list, books, ctxs, earn, *period, capital=CAP, budget=budget)
    return B.stats(curve, trades, CAP), curve, trades


def main():
    books, ctxs, earn = load()
    spy = books["SPY"].px
    rows, curves = [], {}
    for st in CONFIGS:
        if st.kind.startswith("earn") and not any(s in books for s in st.symbols):
            continue
        dv, _, _ = evaluate([st], books, ctxs, earn, DEV)
        ho, hc, ht = evaluate([st], books, ctxs, earn, HOLD)
        curves[st.name] = hc
        rows.append({"strategy": st.name, "dev": dv, "hold": ho, "hold_trades": ht})
        print(st.name, "dev", {k: round(v, 3) for k, v in dv.items()}, "hold", {k: round(v, 3) for k, v in ho.items()}, flush=True)
    # deflated Sharpe on holdout daily returns, across all configs tried
    srs = [r["dev"]["sharpe"] / math.sqrt(252) for r in rows]
    var_sr = float(np.var(srs)) if len(srs) > 1 else 0.0
    def dsr(curve):
        r = curve.pct_change().dropna()
        return float(S.deflated_sharpe(r, len(rows), var_sr)) if len(r) > 30 else float("nan")
    # combo: dev-best of each family that made money on dev
    fam = {}
    for r in rows:
        f = r["strategy"].split()[0]
        if r["dev"]["cagr"] > 0 and (f not in fam or r["dev"]["sharpe"] > fam[f]["dev"]["sharpe"]):
            fam[f] = r
    combo = [st for st in CONFIGS if st.name in {r["strategy"] for r in fam.values()}]
    table = []
    for r in rows:
        h = r["hold"]
        ok = {"Sharpe>=1": h["sharpe"] >= 1, "DD>-25%": h["max_dd"] > -0.25, "CAGR>=15%": h["cagr"] >= 0.15,
              "DSR>=0.95": dsr(curves[r["strategy"]]) >= 0.95, "dev>0": r["dev"]["cagr"] > 0}
        table.append({"strategy": r["strategy"], "dev CAGR": f"{r['dev']['cagr']:.1%}", "dev Sharpe": round(r["dev"]["sharpe"], 2),
                      "hold CAGR": f"{h['cagr']:.1%}", "hold Sharpe": round(h["sharpe"], 2), "hold worst drop": f"{h['max_dd']:.0%}",
                      "hold trades": h["trades"], "hold win %": f"{h['win_rate']:.0%}" if h["trades"] else "-",
                      "$25k ->": f"${h['final']:,.0f}", "$/day": round(h["per_day"], 2),
                      "PASS": "yes" if all(ok.values()) else "no (" + ", ".join(k for k, v in ok.items() if not v) + ")"})
    lines = ["# Round 35: calls and puts on real option prices ($25,000)", "",
             "Rules: [PROTOCOL_ROUND35.md](../PROTOCOL_ROUND35.md). Natural fills (sell at bid, buy at ask), $0.65/contract/leg. "
             f"Dev {DEV[0].date()}–{DEV[1].date()}, holdout {HOLD[0].date()}–{HOLD[1].date()}, each starting at $25,000.", ""]
    spy_h = spy[(spy.index >= HOLD[0]) & (spy.index < HOLD[1])]
    if len(spy_h) > 2:
        yrs = (spy_h.index[-1] - spy_h.index[0]).days / 365.25
        sr = spy_h.pct_change().dropna()
        lines += [f"Benchmark, SPY buy-and-hold on the holdout: {((spy_h.iloc[-1] / spy_h.iloc[0]) ** (1 / yrs) - 1):.1%}/yr, "
                  f"Sharpe {sr.mean() / sr.std() * math.sqrt(252):.2f}, worst drop {(spy_h / spy_h.cummax() - 1).min():.0%}.", ""]
    lines += [pd.DataFrame(table).to_markdown(index=False), ""]
    if combo:
        cs, cc, ct = evaluate(combo, books, ctxs, earn, HOLD)
        cd, _, _ = evaluate(combo, books, ctxs, earn, DEV)
        lines += ["## Combo (dev-best of each family that made money on dev, one account, risk split equally)", "",
                  "Members: " + ", ".join(s.name for s in combo), "",
                  f"Dev: {cd['cagr']:.1%}/yr, Sharpe {cd['sharpe']:.2f}. **Holdout: {cs['cagr']:.1%}/yr, Sharpe {cs['sharpe']:.2f}, "
                  f"worst drop {cs['max_dd']:.0%}, $25k → ${cs['final']:,.0f} (${cs['per_day']:.2f}/day), deflated Sharpe {dsr(cc):.2f}.**", ""]
        if len(ct):
            lines += ["By member (holdout):", "", ct.groupby("strategy")["pnl"].agg(["count", "sum", "mean"]).round(2).to_markdown(), ""]
    for r in rows:
        if len(r["hold_trades"]):
            w = r["hold_trades"].sort_values("pnl").head(3)
            lines += [f"Worst holdout trades, {r['strategy']}: " + "; ".join(f"{x.sym} {x.entry.date()} {x.why} ${x.pnl:,.0f}" for x in w.itertuples())]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
