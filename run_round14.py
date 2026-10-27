"""Round 14 runner (PROTOCOL_ROUND14.md): SPY options, Cboe indexes and TikTok-style trades."""
import time
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round14 as r14
from edge.stats import deflated_sharpe

REPORTS = Path("reports")
N_TRIALS = 269 + len(r14.CBOE) + 4


def yahoo():
    import yfinance as yf
    for wait in (0, 60, 300):
        time.sleep(wait)
        raw = yf.download(["SPY", "^VIX9D", "^VIX1D", "^IRX"], start="2010-06-01", auto_adjust=False,
                          progress=False, threads=False)
        if raw is not None and not raw.empty and raw["Close"]["SPY"].notna().sum() > 3000:
            raw.index = pd.DatetimeIndex(raw.index).tz_localize(None)
            return raw
    raise RuntimeError("Yahoo returned no data")


def stats(eq: pd.Series, periods: int, spy_daily: pd.Series) -> dict:
    eq = eq.dropna()
    r = eq.pct_change().dropna()
    r = pd.concat([pd.Series([eq.iloc[0] - 1], index=eq.index[:1]), r]) if eq.iloc[0] != 1 else r
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    sh = r.mean() / r.std() * np.sqrt(periods) if r.std() > 0 else 0.0
    s = spy_daily[(spy_daily.index > eq.index[0]) & (spy_daily.index <= eq.index[-1])]
    spy_sh = s.mean() / s.std() * np.sqrt(252)
    dsr = deflated_sharpe(r, N_TRIALS, 1 / len(r)) if r.std() > 0 else 0.0
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 and yrs > 0 else -1.0
    mdd = float((eq / eq.cummax() - 1).min())
    checks = {"sharpe>=1": sh >= 1, "dsr>=0.95": dsr >= 0.95, "beats_tbills": cagr > 0.04, "max_dd<=25%": mdd >= -0.25,
              "trades>=30": len(r) >= 30, "beats_spy_sharpe": sh > spy_sh}
    return dict(start=eq.index[0].date(), sharpe=sh, spy_sharpe=spy_sh, cagr=cagr, mdd=mdd, dsr=dsr,
                usd=1000 * eq.iloc[-1], n=len(r), checks=checks, ok=all(checks.values()))


def main():
    raw = yahoo()
    close, opn = raw["Close"]["SPY"].dropna(), raw["Open"]["SPY"].dropna()
    spy_daily = raw["Adj Close"]["SPY"].pct_change().dropna()
    rate = (raw["Close"]["^IRX"] / 100).ffill().reindex(close.index).ffill().fillna(0.0)
    vix9d = raw["Close"]["^VIX9D"].reindex(close.index)
    vix1d_open = raw["Open"]["^VIX1D"].reindex(close.index)
    rows, ledgers = [], {}

    for name in r14.CBOE:
        s = r14.cboe_index(name)
        s = s[s.index >= r14.START]
        if len(s) < 500:
            rows.append((f"Cboe {name}", None, f"no data ({len(s)} rows)"))
            continue
        eq = s / s.iloc[0]
        st = stats(eq, 252, spy_daily)
        st["win"] = (eq.pct_change() > 0).mean()
        rows.append((f"Cboe {name}", st, ""))

    b1 = r14.b1_weekly_calls(close[close.index >= r14.START], vix9d, rate)
    b2 = r14.b2_0dte_calls(opn, close, vix1d_open, rate)
    b3 = r14.b3_0dte_condor(opn, close, vix1d_open, rate)
    b4 = r14.b4_weekly_puts(close[close.index >= r14.START], vix9d, rate)
    for tag, t, eq_fn, per in (("B1 buy weekly 2% OTM calls", b1, r14.equity_buyer, 52),
                               ("B2 buy 0DTE 0.5% OTM calls", b2, r14.equity_buyer, 252),
                               ("B3 sell 0DTE iron condor", b3, r14.equity_seller, 252),
                               ("B4 sell weekly 2% OTM puts", b4, r14.equity_seller, 52)):
        if t.empty:
            rows.append((tag, None, "no trades"))
            continue
        eq = eq_fn(t)
        st = stats(pd.concat([pd.Series([1.0], index=[t["entry"].iloc[0]]), eq]), per, spy_daily)
        st["win"] = (t["ret"] > 0).mean()
        if "payoff" in t:
            st["best"] = f"{(t['payoff'] / t['cost']).max():.0f}x"
            st["x10"] = int(((t["payoff"] / t["cost"]) >= 10).sum())
        rows.append((tag, st, ""))
        ledgers[tag] = t

    lines = ["# Round 14: SPY options, honestly counted", "",
             f"Rules: [PROTOCOL_ROUND14.md](../PROTOCOL_ROUND14.md). Deflated over {N_TRIALS} trials. Part B is "
             "Black-Scholes priced from VIX9D / VIX1D with a 5% half-spread; it ignores skew, which flatters call "
             "buying and penalises put selling.", "",
             "| Strategy | From | Win rate | Sharpe | SPY Sharpe | Yearly | Worst drop | $1,000 → | Deflated Sharpe | Best trade | 10x+ trades | Pass |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|"]
    for tag, st, note in rows:
        if st is None:
            lines.append(f"| {tag} | {note} | | | | | | | | | | |")
            continue
        lines.append(f"| {tag} | {st['start']} | {st['win']:.0%} | {st['sharpe']:.2f} | {st['spy_sharpe']:.2f} | "
                     f"{st['cagr']:+.1%} | {st['mdd']:.0%} | ${st['usd']:,.0f} | {st['dsr']:.3f} | "
                     f"{st.get('best', '')} | {st.get('x10', '')} | **{'PASS' if st['ok'] else 'FAIL'}** |")
    lines += ["", "Failed checks per strategy:", ""]
    for tag, st, _ in rows:
        if st is not None:
            bad = [k for k, v in st["checks"].items() if not v]
            lines.append(f"- {tag}: {', '.join(bad) or 'none'}")
    if "B1 buy weekly 2% OTM calls" in ledgers:
        t = ledgers["B1 buy weekly 2% OTM calls"]
        top = t.assign(multiple=t["payoff"] / t["cost"]).nlargest(5, "multiple")
        lines += ["", "## The screenshots: B1's five best weeks (each would make a viral post)", "",
                  "| Bought | Expired | Multiple |", "|---|---|---:|"] + \
                 [f"| {x.entry.date()} | {x.exit.date()} | {x.multiple:.1f}x |" for x in top.itertuples()] + \
                 ["", f"Weeks that expired worthless: {(t['payoff'] == 0).mean():.0%} of {len(t)}."]
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "ROUND14.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
