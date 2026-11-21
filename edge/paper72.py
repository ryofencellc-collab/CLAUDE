"""Round 72 live paper tracker (PROTOCOL_ROUND72.md, paper section): SPY 10-delta put credit spreads, Mon/Wed/Fri,
25-50 days to expiry, managed (50% profit / 2x-loss stop / 21 days left), 70% open-risk cap, only above the 200-day.
Real Yahoo SPY quotes; fills at natural prices (sell at bid, buy at ask), $0.65/contract/leg. Run once each weekday near 15:45 ET.
Usage: python -m edge.paper72 [--force-entry] [--dry]"""
import json, math, os, sys
from datetime import datetime, timezone
import numpy as np, pandas as pd, yfinance as yf
from edge.odte import _bs, _iv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "paper", "r72_state.json")
LEDGER = os.path.join(ROOT, "paper", "r72_trades.csv")
DAILY = os.path.join(ROOT, "paper", "r72_daily.csv")
REPORT = os.path.join(ROOT, "paper", "ROUND72_PAPER.md")
CAPITAL, CAP, SLOTS, DELTA, COMM = 25_000.0, 0.70, 15, 0.10, 0.65
DTE = (25, 50, 35)
ET = "America/New_York"


def load_state():
    if os.path.exists(STATE): return json.load(open(STATE))
    return dict(cash=CAPITAL, pos=[], started=None)


def chain(tk, exp, S, now):
    oc = tk.option_chain(exp).puts
    T = max((pd.Timestamp(exp + " 16:00", tz=ET) - now).total_seconds() / (365 * 86400), 1e-4)
    rows = []
    for r in oc.itertuples():
        b, a = float(r.bid or 0), float(r.ask or 0)
        if a <= 0 or a < b: continue
        iv = _iv(S, float(r.strike), T, (b + a) / 2, "P")
        d = _bs(S, float(r.strike), T, iv, "P")[0] if iv == iv else float("nan")
        rows.append(dict(K=float(r.strike), bid=b, ask=a, delta=d))
    return pd.DataFrame(rows).sort_values("K") if rows else pd.DataFrame(columns=["K", "bid", "ask", "delta"])


def quote(tk, exp, K, S, now, cache):
    if exp not in cache: cache[exp] = chain(tk, exp, S, now)
    c = cache[exp]; x = c[c.K == K]
    return (float(x.bid.iloc[0]), float(x.ask.iloc[0])) if len(x) else None


def run(force_entry=False, dry=False, ignore_trend=False):
    now = pd.Timestamp.now(tz=ET); today = now.date().isoformat()
    st = load_state(); st["started"] = st.get("started") or today
    tk = yf.Ticker("SPY")
    exps = [e for e in tk.options]
    hist = tk.history(period="400d")["Close"].dropna()
    try:      # the option chain's own underlying price (daily history can lag a day)
        S = float(tk.option_chain(exps[0]).underlying["regularMarketPrice"])
    except Exception:
        S = float(hist.iloc[-1])
    if hist.index[-1].date() < now.date(): hist = pd.concat([hist, pd.Series([S], index=[hist.index[-1] + pd.Timedelta(days=1)])])
    sma200 = float(hist.iloc[-200:].mean())
    cache, log, trades = {}, [], []
    # 1) manage open positions
    keep = []
    for p in st["pos"]:
        exp_day = pd.Timestamp(p["exp"]).date()
        if now.date() >= exp_day:
            val = -max(p["Ks"] - S, 0) + max(p["Kl"] - S, 0)          # intrinsic of short put spread at expiry (per share)
            done, why, close_cost = True, "expiry", -val
        else:
            qs, ql = quote(tk, p["exp"], p["Ks"], S, now, cache), quote(tk, p["exp"], p["Kl"], S, now, cache)
            if qs is None or ql is None:
                keep.append(p); log.append(f"no quote for {p['exp']} {p['Ks']}/{p['Kl']}; holding"); continue
            close_cost = qs[1] - ql[0]                                    # buy back short at ask, sell long at bid
            p["mark"] = (qs[0] + qs[1]) / 2 - (ql[0] + ql[1]) / 2
            dte = (exp_day - now.date()).days
            done, why = False, ""
            if close_cost <= 0.5 * p["credit"]: done, why = True, "50% profit"
            elif close_cost >= 3 * p["credit"]: done, why = True, "stop 2x"
            elif dte <= 21: done, why = True, "21 days left"
        if done:
            comm = 0 if why == "expiry" else COMM * 2 * p["qty"]
            st["cash"] -= close_cost * 100 * p["qty"] + comm
            pnl = (p["credit"] - close_cost) * 100 * p["qty"] - COMM * 2 * p["qty"] - comm
            trades.append(dict(entry=p["entry"], exit=today, exp=p["exp"], Ks=p["Ks"], Kl=p["Kl"], qty=p["qty"], credit=p["credit"], close=round(close_cost, 2), why=why, pnl=round(pnl, 2)))
        else:
            keep.append(p)
    st["pos"] = keep
    equity = st["cash"] - sum(p.get("mark", p["credit"]) * 100 * p["qty"] for p in st["pos"])
    # 2) entry (Mon/Wed/Fri, above the 200-day)
    entry_day = force_entry or now.weekday() in (0, 2, 4)
    if entry_day and (S > sma200 or ignore_trend):
        ok = [e for e in exps if DTE[0] <= (pd.Timestamp(e).date() - now.date()).days <= DTE[1]]
        if ok:
            e = min(ok, key=lambda x: abs((pd.Timestamp(x).date() - now.date()).days - DTE[2]))
            c = chain(tk, e, S, now); c = c[c.bid > 0].dropna(subset=["delta"])
            if len(c) > 2:
                i = int((c.delta.abs() - DELTA).abs().to_numpy().argmin()); ks = c.K.tolist()
                if i > 0:
                    short, long = c.iloc[i], c.iloc[i - 1]
                    credit = float(short.bid - long.ask); width = float(short.K - long.K)
                    mid_credit = float((short.bid + short.ask) / 2 - (long.bid + long.ask) / 2)
                    ml = (width - credit) * 100
                    risk_open = sum((p["Ks"] - p["Kl"] - p["credit"]) * 100 * p["qty"] for p in st["pos"])
                    room = CAP * equity - risk_open
                    qty = int(min(CAP / SLOTS * equity, room) // ml) if credit > 0 and ml > 0 else 0
                    if qty < 1 and credit > 0 and 0 < ml <= room: qty = 1
                    if qty >= 1:
                        st["cash"] += credit * 100 * qty - COMM * 2 * qty
                        st["pos"].append(dict(entry=today, exp=e, Ks=float(short.K), Kl=float(long.K), qty=qty, credit=round(credit, 2), mark=credit,
                                              short_delta=round(float(short.delta), 3), mid_credit=round(mid_credit, 2)))
                        log.append(f"OPEN {qty}x {e} {short.K}/{long.K} credit {credit:.2f} (delta {short.delta:.3f}), max loss ${ml * qty:,.0f}")
                    else:
                        log.append(f"no entry: natural credit {credit:.2f} (mid {mid_credit:.2f}) on {short.K}/{long.K}, max loss {ml:.0f}, room {room:.0f}")
        else:
            log.append("no expiry 25-50 days out")
    elif entry_day:
        log.append(f"no entry: SPY {S:.2f} below 200-day {sma200:.2f}")
    equity = st["cash"] - sum(p.get("mark", p["credit"]) * 100 * p["qty"] for p in st["pos"])
    print(today, f"SPY {S:.2f} sma200 {sma200:.2f} equity {equity:,.2f} open {len(st['pos'])}", *log, *[str(t) for t in trades], sep="\n  ")
    if dry: return
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, "w"), indent=1)
    if trades: pd.DataFrame(trades).to_csv(LEDGER, mode="a", header=not os.path.exists(LEDGER), index=False)
    pd.DataFrame([dict(day=today, spy=round(S, 2), equity=round(equity, 2), open=len(st["pos"]), note="; ".join(log))]).to_csv(DAILY, mode="a", header=not os.path.exists(DAILY), index=False)
    summary(st, equity)


def summary(st, equity):
    T = pd.read_csv(LEDGER) if os.path.exists(LEDGER) else pd.DataFrame(columns=["pnl"])
    D = pd.read_csv(DAILY) if os.path.exists(DAILY) else pd.DataFrame(columns=["equity"])
    dd = float((D.equity / D.equity.cummax() - 1).min() * 100) if len(D) else 0.0
    out = ["# Round 72 live paper: SPY 10-delta put credit spreads, Mon/Wed/Fri", "", "Rules: [PROTOCOL_ROUND72.md](../PROTOCOL_ROUND72.md). Real Yahoo quotes, natural fills, $25,000 paper account. No real money.", "",
           f"Started {st['started']}. Equity **${equity:,.2f}** ({100 * (equity / CAPITAL - 1):+.2f}%). Closed trades: {len(T)}, wins {int((T.pnl > 0).sum()) if len(T) else 0}, "
           f"P&L ${T.pnl.sum() if len(T) else 0:,.2f}. Open spreads: {len(st['pos'])}. Max drawdown so far {dd:.1f}%.", "",
           "## Open", "", pd.DataFrame(st["pos"]).to_markdown(index=False) if st["pos"] else "none", "", "## Closed", "", T.tail(30).to_markdown(index=False) if len(T) else "none", ""]
    open(REPORT, "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    run(force_entry="--force-entry" in sys.argv, dry="--dry" in sys.argv, ignore_trend="--test-ignore-trend" in sys.argv and "--dry" in sys.argv)
