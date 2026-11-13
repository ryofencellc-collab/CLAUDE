"""Round 49 (PROTOCOL_ROUND49.md): the options wheel on real EOD chains."""
import math
from pathlib import Path
import numpy as np, pandas as pd
from edge import optbt as B

D = Path("data/opt")
SYMS = ("SPY", "AAPL", "MSFT", "NVDA", "AMZN", "META", "TSLA", "GOOGL")
DEV = (pd.Timestamp("2020-03-01"), pd.Timestamp("2024-01-01"))
HOLD = (pd.Timestamp("2024-01-01"), pd.Timestamp("2026-12-01"))
ADJ, FACT = {}, {}
VARIANTS = {"W1 wheel d0.30": (0.30, False), "W2 wheel d0.16": (0.16, False), "W3 wheel d0.30, calls >= cost": (0.30, True)}


def pick(book, d, cp, delta, min_strike=None):
    t = book.by_day.get(d)
    if t is None: return None
    e = B.pick_exp(t, d, 25, 45, 30)
    if e is None: return None
    s = B.side_tbl(t, e, cp)
    if min_strike is not None:
        s = s[s["strike"] >= min_strike]
    r = B.by_delta(s, delta)
    if r is None or not r["bid"] > 0: return None
    return e, float(r["strike"]), float(r["bid"])


def parity_spot(chain: pd.DataFrame) -> pd.Series:
    """Spot implied by put-call parity at the nearest expiry >= 5 days: the strike where call and put mids are closest,
    plus (call mid - put mid). It is on the same (unadjusted) basis as the strikes, unlike Yahoo's split-adjusted Close."""
    c = chain.dropna(subset=["bid", "ask", "strike"]).copy()
    c = c[(c.ask >= c.bid) & (c.bid > 0)]
    c["mid"] = (c.bid + c.ask) / 2
    c["cp"] = np.where(c.call_put.str.lower().str.startswith("c"), "C", "P")
    c = c[(c.expiration - c.date).dt.days >= 5]
    first = c.groupby("date").expiration.transform("min")
    c = c[c.expiration == first]
    w = c.pivot_table(index=["date", "strike"], columns="cp", values="mid").dropna()
    w["gap"] = (w.C - w.P).abs()
    best = w.loc[w.groupby(level="date").gap.idxmin()]
    out = pd.Series((best.index.get_level_values("strike") + best.C - best.P).to_numpy(), index=best.index.get_level_values("date"))
    return out.sort_index()


def split_factor(raw: pd.Series, adj: pd.Series) -> pd.Series:
    """raw/adjusted price ratio; a day-to-day fall of more than 1.4x marks an n-for-1 split."""
    return raw / adj.reindex(raw.index).ffill()      # same-day ratio: a split shows up on the split day itself


def wheel(book, a, b, delta, protect, f=None):
    days = [d for d in book.days if a <= d < b]
    if not days: return pd.Series(dtype=float), 0
    s0 = book.spot(days[0]); cash = 100 * s0; shares = 0; basis = None; opt = None; last_mark = 0.0   # opt = (exp, strike, cp)
    eq, n_tr = [], 0
    prev_f = None
    for d in days:
        if f is not None:
            fd = f.get(d, np.nan)
            if prev_f is not None and np.isfinite(fd) and np.isfinite(prev_f) and fd / prev_f < 1 / 1.4:
                k = round(prev_f / fd)                 # n-for-1 split: more shares, lower basis; open option closed at its last mark
                shares *= k; basis = basis / k if basis else basis
                if opt is not None:
                    cash -= last_mark; opt = None
            prev_f = fd if np.isfinite(fd) else prev_f
        if opt is not None and d >= opt[0]:
            e, k, cp = opt; s = book.spot(e)
            if cp == "P" and s < k:
                cash -= 100 * k; shares = 100; basis = k
            elif cp == "C" and s > k:
                cash += 100 * k; shares = 0; basis = None
            opt = None
        if opt is None:
            cp = "C" if shares else "P"
            p = pick(book, d, cp, delta, basis if (protect and cp == "C") else None)
            if p is not None:
                e, k, bid = p
                cash += 100 * bid - B.COMM; opt = (e, k, cp); n_tr += 1
        mark = 0.0
        if opt is not None:
            q = book.quote(d, opt)
            if q is not None: mark = 100 * (q[0] + q[1]) / 2
            else: mark = 100 * B.intrinsic((opt[0], opt[1], opt[2], 1), book.spot(d))
        last_mark = mark
        eq.append(cash + shares * book.spot(d) - mark)
    return pd.Series(eq, index=days) / (100 * s0), n_tr


def stats(curve):
    r = curve.pct_change().dropna()
    if len(r) < 20: return dict(cagr=np.nan, sharpe=np.nan, dd=np.nan)
    yrs = (curve.index[-1] - curve.index[0]).days / 365.25
    return dict(cagr=(curve.iloc[-1] / curve.iloc[0]) ** (1 / yrs) - 1, sharpe=r.mean() / r.std() * math.sqrt(252), dd=(curve / curve.cummax() - 1).min())


def main():
    books = {}
    for s in SYMS:
        p = D / f"{s}.pkl"
        if not p.exists(): print("missing", s); continue
        ch = pd.read_pickle(p)
        adj = pd.read_pickle(D / f"{s}_px.pkl")["Close"]; adj.index = pd.to_datetime(adj.index).tz_localize(None)
        raw = parity_spot(ch)
        books[s] = B.Book(ch, raw)
        ADJ[s], FACT[s] = adj, split_factor(raw, adj)
        print(s, "parity spot", raw.index.min().date(), raw.index.max().date(), "factor range", round(FACT[s].min(), 3), round(FACT[s].max(), 3), flush=True)
    rows, port = [], {}
    for name, (dl, prot) in VARIANTS.items():
        for per, (a, b) in (("dev", DEV), ("holdout", HOLD)):
            curves, bh = [], []
            for s, bk in books.items():
                c, n = wheel(bk, a, b, dl, prot, FACT[s])
                if c.empty: continue
                px = ADJ[s].reindex(c.index).ffill().bfill()             # buy-and-hold on split-adjusted prices
                h = px / px.iloc[0]
                w, hh = stats(c), stats(h)
                rows.append(dict(variant=name, period=per, symbol=s, trades=n, wheel_CAGR=f"{w['cagr']:.1%}", wheel_Sharpe=round(w["sharpe"], 2),
                                 wheel_drop=f"{w['dd']:.1%}", hold_CAGR=f"{hh['cagr']:.1%}", hold_Sharpe=round(hh["sharpe"], 2), hold_drop=f"{hh['dd']:.1%}"))
                curves.append(c.pct_change().fillna(0)); bh.append(h.pct_change().fillna(0))
            ew = (1 + pd.concat(curves, axis=1).fillna(0).mean(axis=1)).cumprod()
            eb = (1 + pd.concat(bh, axis=1).fillna(0).mean(axis=1)).cumprod()
            port[(name, per)] = (stats(ew), stats(eb))
    out = ["# Round 49: the options wheel on real end-of-day chains", "",
           "Rules: [PROTOCOL_ROUND49.md](../PROTOCOL_ROUND49.md). One cash-secured contract per symbol; natural fills; $0.65/contract.", "",
           "## Equal-weight portfolio of the 8 symbols", "", "| variant | period | wheel CAGR | wheel Sharpe | wheel drop | buy-hold CAGR | buy-hold Sharpe | buy-hold drop |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    passed = []
    for (name, per), (w, h) in port.items():
        out.append(f"| {name} | {per} | {w['cagr']:.1%} | {w['sharpe']:.2f} | {w['dd']:.1%} | {h['cagr']:.1%} | {h['sharpe']:.2f} | {h['dd']:.1%} |")
    for name in VARIANTS:
        (wd, hd), (wh, hh) = port[(name, "dev")], port[(name, "holdout")]
        if wh["sharpe"] >= 1 and wh["cagr"] >= 0.15 and wh["sharpe"] > hh["sharpe"] and wd["sharpe"] > hd["sharpe"]:
            passed.append(name)
    out += ["", f"**Passing: {', '.join(passed) or 'none'}.**", "", "## Per symbol", "", pd.DataFrame(rows).to_markdown(index=False)]
    Path("reports/ROUND49.md").write_text("\n".join(out) + "\n"); print("\n".join(out[:20]))


if __name__ == "__main__":
    main()
