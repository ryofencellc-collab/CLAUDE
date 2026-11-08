"""Round 35 options backtester (PROTOCOL_ROUND35.md): real EOD chains, natural fills, $0.65/contract/leg."""
import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

COMM = 0.65
MULT = 100


class Book:
    """One symbol's chains: fast quote lookup and per-day option tables."""

    def __init__(self, chain: pd.DataFrame, px: pd.Series):
        c = chain.dropna(subset=["bid", "ask", "strike"]).copy()
        c = c[(c["ask"] >= c["bid"]) & (c["ask"] > 0)]
        c["cp"] = np.where(c["call_put"].str.lower().str.startswith("c"), "C", "P")
        self.days = sorted(c["date"].unique())
        self.by_day = {d: g for d, g in c.groupby("date")}
        self.q = {(d, e, k, cp): (b, a, de) for d, e, k, cp, b, a, de in
                  zip(c["date"], c["expiration"], c["strike"], c["cp"], c["bid"], c["ask"], c["delta"])}
        self.px = px.sort_index()
        self._pi, self._pv = self.px.index.values, self.px.to_numpy(dtype=float)
        self._next = {d: n for d, n in zip(self.days, self.days[1:])}

    def spot(self, d):
        i = np.searchsorted(self._pi, np.datetime64(d), side="right") - 1
        return float(self._pv[i]) if i >= 0 else float("nan")

    def quote(self, d, leg):
        return self.q.get((d, leg[0], leg[1], leg[2]))


def intrinsic(leg, s):
    e, k, cp, n = leg
    return n * (max(s - k, 0.0) if cp == "C" else max(k - s, 0.0))


@dataclass
class Pos:
    sym: str
    legs: list            # (expiration, strike, "C"/"P", +1 long / -1 short) per unit
    qty: int
    entry: pd.Timestamp
    open_cash: float      # per unit: + credit received / - debit paid (natural)
    max_loss: float       # per unit, dollars
    kind: str             # "credit" | "debit" | "event"
    exit_on: pd.Timestamp | None = None
    last_mark: float = 0.0
    tag: str = ""
    manage: bool = True


def open_cash(book, d, legs):
    tot = 0.0
    for e, k, cp, n in legs:
        q = book.quote(d, (e, k, cp))
        if q is None or q[0] <= 0 and n < 0:
            return None
        tot += -n * (q[1] if n > 0 else q[0])     # buy longs at the ask, sell shorts at the bid
    return tot


def close_value(book, d, legs, natural=True):
    """Per-unit value of closing now (long legs sold at the bid, shorts bought back at the ask)."""
    tot = 0.0
    for e, k, cp, n in legs:
        if d >= e:
            tot += intrinsic((e, k, cp, n), book.spot(e))
            continue
        q = book.quote(d, (e, k, cp))
        if q is None:
            return None
        b, a, _ = q
        tot += n * ((b if n > 0 else a) if natural else (b + a) / 2)
    return tot


# ------------------------------------------------------------------ leg pickers
def pick_exp(day_tbl, d, lo, hi, target):
    exps = sorted(day_tbl["expiration"].unique())
    ok = [e for e in exps if lo <= (e - d).days <= hi]
    return min(ok, key=lambda e: abs((e - d).days - target)) if ok else None


def side_tbl(day_tbl, e, cp):
    t = day_tbl[(day_tbl["expiration"] == e) & (day_tbl["cp"] == cp)].sort_values("strike")
    return t[t["bid"] > 0]


def by_delta(t, target):
    if t.empty or t["delta"].isna().all():
        return None
    return t.iloc[(t["delta"].abs() - target).abs().argsort().iloc[0]]


def vertical(book, d, e, cp, short_delta, credit=True):
    """Short ~delta strike + next strike further OTM (credit) or long ~delta + next strike further OTM (debit)."""
    t = side_tbl(book.by_day[d], e, cp)
    r = by_delta(t, short_delta)
    if r is None:
        return None
    ks = list(t["strike"])
    i = ks.index(r["strike"])
    j = i - 1 if cp == "P" else i + 1
    if not 0 <= j < len(ks):
        return None
    k1, k2 = r["strike"], ks[j]
    if credit:
        legs = [(e, k1, cp, -1), (e, k2, cp, +1)]
    else:
        legs = [(e, k1, cp, +1), (e, k2, cp, -1)]
    return legs, abs(k1 - k2)


# ------------------------------------------------------------------ strategies
@dataclass
class Strat:
    name: str
    kind: str                       # put_spread | condor | call_spread | call_debit | put_debit | earn_fly | earn_condor | earn_straddle
    delta: float = 0.30
    filt: tuple = ()                # "trend", "ivr", "downtrend", "contango", "breakout", "breakdown"
    risk: float = 0.05
    symbols: tuple = ("SPY",)
    manage: bool = True             # False: hold credit spreads to expiry (no profit target, stop or 21-day exit)


def entries(st: Strat, book, d, ctx) -> list:
    """Candidate new positions for strategy st on day d (per unit). Returns list of (legs, open_cash, max_loss, kind, exit_on)."""
    tbl = book.by_day.get(d)
    if tbl is None:
        return []
    s = book.spot(d)
    f = set(st.filt)
    sma200, sma50 = ctx["sma200"].get(d, np.nan), ctx["sma50"].get(d, np.nan)
    if "trend" in f and not s > sma200:
        return []
    if "downtrend" in f and not s < sma200:
        return []
    if "ivr" in f and not ctx["ivr"].get(d, np.nan) > 0.30:
        return []
    if "contango" in f and not ctx["contango"].get(d, False):
        return []
    if "breakout" in f and not (s > sma200 and ctx["hi55"].get(d, False)):
        return []
    if "breakdown" in f and not (s < sma200 and ctx["lo55"].get(d, False)):
        return []
    out = []
    if st.kind in ("put_spread", "call_spread", "condor"):
        e = pick_exp(tbl, d, 25, 50, 35)
        if e is None:
            return []
        legs, widths = [], []
        for cp in (("P",) if st.kind == "put_spread" else ("C",) if st.kind == "call_spread" else ("P", "C")):
            v = vertical(book, d, e, cp, st.delta, credit=True)
            if v is None:
                return []
            legs += v[0]
            widths.append(v[1])
        oc = open_cash(book, d, legs)
        if oc is None or oc <= 0:
            return []
        out.append((legs, oc, (max(widths) - oc) * MULT, "credit", None))
    elif st.kind in ("call_debit", "put_debit"):
        e = pick_exp(tbl, d, 45, 70, 55)
        if e is None:
            return []
        v = vertical(book, d, e, "C" if st.kind == "call_debit" else "P", 0.50, credit=False)
        if v is None:
            return []
        oc = open_cash(book, d, v[0])
        if oc is None or oc >= 0:
            return []
        out.append((v[0], oc, -oc * MULT, "debit", None))
    return out


def earnings_entries(st: Strat, book, d, exit_day):
    tbl = book.by_day.get(d)
    if tbl is None:
        return []
    s = book.spot(d)
    exps = sorted(e for e in tbl["expiration"].unique() if e > exit_day)
    if not exps:
        return []
    e = exps[0]
    calls, puts = side_tbl(tbl, e, "C"), side_tbl(tbl, e, "P")
    if calls.empty or puts.empty:
        return []
    k = min(set(calls["strike"]) & set(puts["strike"]), key=lambda x: abs(x - s), default=None)
    if k is None:
        return []
    if st.kind == "earn_straddle":
        legs = [(e, k, "C", +1), (e, k, "P", +1)]
        oc = open_cash(book, d, legs)
        return [] if oc is None or oc >= 0 else [(legs, oc, -oc * MULT, "event", exit_day)]
    if st.kind == "earn_fly":
        kc = min(calls["strike"], key=lambda x: abs(x - s * 1.08))
        kp = min(puts["strike"], key=lambda x: abs(x - s * 0.92))
        if not (kc > k > kp):
            return []
        legs = [(e, k, "C", -1), (e, k, "P", -1), (e, kc, "C", +1), (e, kp, "P", +1)]
        w = max(kc - k, k - kp)
    else:  # earn_condor
        vp, vc = vertical(book, d, e, "P", 0.16), vertical(book, d, e, "C", 0.16)
        if vp is None or vc is None:
            return []
        legs, w = vp[0] + vc[0], max(vp[1], vc[1])
    oc = open_cash(book, d, legs)
    if oc is None or oc <= 0:
        return []
    return [(legs, oc, (w - oc) * MULT, "event", exit_day)]


def context(book, vix=None):
    px = book.px["Close"] if isinstance(book.px, pd.DataFrame) else book.px
    sma200, sma50 = px.rolling(200).mean(), px.rolling(50).mean()
    hi55 = px >= px.rolling(55).max()
    lo55 = px <= px.rolling(55).min()
    atm = {}
    for d in book.days:
        t = book.by_day[d]
        e = pick_exp(t, d, 20, 60, 35)
        if e is None:
            continue
        s = book.spot(d)
        x = t[t["expiration"] == e]
        if x.empty or not np.isfinite(s):
            continue
        k = x.iloc[(x["strike"] - s).abs().argsort().iloc[0]]["strike"]
        v = x[x["strike"] == k]["vol"].mean()
        if np.isfinite(v):
            atm[d] = v
    iv = pd.Series(atm).sort_index()
    lo, hi = iv.rolling(252, min_periods=120).min(), iv.rolling(252, min_periods=120).max()
    ivr = ((iv - lo) / (hi - lo)).shift(1)
    ctx = {"sma200": sma200.to_dict(), "sma50": sma50.to_dict(), "hi55": hi55.to_dict(), "lo55": lo55.to_dict(),
           "ivr": ivr.to_dict(), "contango": {}}
    if vix is not None:
        ctx["contango"] = (vix["VIX"] < vix["VIX3M"]).to_dict()
    return ctx


# ------------------------------------------------------------------ engine
def run(strats: list, books: dict, ctxs: dict, earn: dict, start, end, capital=25_000.0, budget=None):
    """Simulate strategies in one account. budget: per-strategy share of the 30% open-risk cap (default equal)."""
    budget = budget or {st.name: 1.0 / len(strats) for st in strats}
    cash, pos, trades, curve = capital, [], [], {}
    all_days = sorted({d for b in books.values() for d in b.days if start <= d < end})
    week_seen = set()
    for d in all_days:
        # 1) manage and exit
        keep = []
        for p in pos:
            b = books[p.sym]
            exp = min(l[0] for l in p.legs)
            mark_nat = close_value(b, d, p.legs, natural=True)
            mark_mid = close_value(b, d, p.legs, natural=False)
            if mark_mid is not None:
                p.last_mark = mark_mid
            done, why = False, ""
            if d >= exp:
                val = sum(intrinsic(l, b.spot(exp)) for l in p.legs)
                done, why, mark_nat = True, "expiry", val
            elif mark_nat is not None:
                if p.kind == "event" and p.exit_on is not None and d >= p.exit_on:
                    done, why = True, "event over"
                elif p.kind == "credit" and p.manage:
                    cost = -mark_nat
                    if cost <= 0.5 * p.open_cash:
                        done, why = True, "50% profit"
                    elif cost >= 3 * p.open_cash:
                        done, why = True, "stop 2x"
                    elif (exp - d).days <= 21:
                        done, why = True, "21 days left"
                elif p.kind == "debit":
                    debit = -p.open_cash
                    sma50 = ctxs[p.sym]["sma50"].get(d, np.nan)
                    s = b.spot(d)
                    trend_broke = (s < sma50) if any(l[2] == "C" and l[3] > 0 for l in p.legs) else (s > sma50)
                    if mark_nat >= 2 * debit or mark_nat <= 0.5 * debit or (exp - d).days <= 14 or trend_broke:
                        done, why = True, "debit exit"
            if done:
                legs_n = len(p.legs)
                comm = 0 if why == "expiry" else COMM * legs_n * p.qty
                cash += mark_nat * MULT * p.qty - comm
                pnl = (p.open_cash + mark_nat) * MULT * p.qty - 2 * COMM * legs_n * p.qty + (COMM * legs_n * p.qty if why == "expiry" else 0)
                trades.append({"strategy": p.tag, "sym": p.sym, "entry": p.entry, "exit": d, "why": why, "qty": p.qty,
                               "pnl": pnl, "max_loss": p.max_loss * p.qty})
            else:
                keep.append(p)
        pos = keep
        equity = cash + sum(p.last_mark * MULT * p.qty for p in pos)
        # 2) new entries
        wk = (d.isocalendar().year, d.isocalendar().week)
        weekly = wk not in week_seen
        week_seen.add(wk)
        open_risk = {}
        for p in pos:
            open_risk[p.tag] = open_risk.get(p.tag, 0.0) + p.max_loss * p.qty
        for st in strats:
            cands = []
            if st.kind.startswith("earn"):
                for sym in st.symbols:
                    b = books.get(sym)
                    if b is None or d not in b.by_day:
                        continue
                    nxt = b._next.get(d)
                    for E in earn.get(sym, []):
                        if nxt is not None and d < E <= nxt:              # d is the last trading day before earnings
                            exit_day = b._next.get(nxt) if nxt == E else nxt
                            if exit_day is not None and (exit_day - d).days <= 6:
                                cands += [(sym, *c) for c in earnings_entries(st, b, d, exit_day)]
            elif weekly:
                for sym in st.symbols:
                    b = books.get(sym)
                    if b is not None and d in b.by_day:
                        cands += [(sym, *c) for c in entries(st, b, d, ctxs[sym])]
            cap_total = 0.30 * equity * budget[st.name]
            for sym, legs, oc, ml, kind, exit_on in cands:
                if ml <= 0:
                    continue
                room = cap_total - open_risk.get(st.name, 0.0)
                qty = int(min(st.risk * equity, room) // ml)
                if qty < 1:
                    continue
                comm = COMM * len(legs) * qty
                cash += oc * MULT * qty - comm
                p = Pos(sym, legs, qty, d, oc, ml, kind, exit_on, last_mark=-oc, tag=st.name, manage=st.manage)
                mm = close_value(books[sym], d, legs, natural=False)
                p.last_mark = mm if mm is not None else -oc
                pos.append(p)
                open_risk[st.name] = open_risk.get(st.name, 0.0) + ml * qty
        curve[d] = cash + sum(p.last_mark * MULT * p.qty for p in pos)
    return pd.Series(curve).sort_index(), pd.DataFrame(trades)


def stats(curve: pd.Series, trades: pd.DataFrame, capital: float) -> dict:
    if curve.empty:
        return {"final": capital, "cagr": 0.0, "sharpe": 0.0, "max_dd": 0.0, "trades": 0, "win_rate": np.nan, "per_day": 0.0}
    r = curve.pct_change().dropna()
    years = max((curve.index[-1] - curve.index[0]).days / 365.25, 1 / 365)
    final = float(curve.iloc[-1])
    cagr = (final / capital) ** (1 / years) - 1 if final > 0 else -1.0
    sharpe = float(r.mean() / r.std() * math.sqrt(252)) if r.std() > 0 else 0.0
    dd = float((curve / curve.cummax() - 1).min())
    return {"final": final, "cagr": cagr, "sharpe": sharpe, "max_dd": dd, "trades": len(trades),
            "win_rate": float((trades["pnl"] > 0).mean()) if len(trades) else np.nan,
            "per_day": (final - capital) / max((curve.index[-1] - curve.index[0]).days, 1)}
