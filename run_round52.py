"""Round 52 (PROTOCOL_ROUND52.md): NY/Asia session setups on S&P & Nasdaq 1-minute bars, scored as prop-firm accounts."""
import math, os
import numpy as np, pandas as pd
from edge.intraday import load_nq

SPLIT = pd.Timestamp("2021-01-01")
INSTR = {"S&P (MES)": dict(pair="SPXUSD", pt=5.0, slip=0.5), "Nasdaq (MNQ)": dict(pair="NSXUSD", pt=2.0, slip=1.25)}
COMM, RISK, MAXC = 1.24, 250.0, 15
T = lambda s: pd.Timestamp(s).time()


def trade_path(o, h, l, c, i0, side, stop, tgt, last):
    """Enter at o[i0]; walk bars i0..last; returns (exit price, exit index)."""
    e = o[i0]
    for j in range(i0, last + 1):
        if side > 0:
            if l[j] <= stop: return (min(o[j], stop) if j > i0 else stop), j
            if tgt is not None and h[j] >= tgt: return (max(o[j], tgt) if j > i0 else tgt), j
        else:
            if h[j] >= stop: return (max(o[j], stop) if j > i0 else stop), j
            if tgt is not None and l[j] <= tgt: return (min(o[j], tgt) if j > i0 else tgt), j
    return c[last], last


def session_trades(bars, setup):
    out = []
    idx = bars.index; o, h, l, c = (bars[k].to_numpy() for k in ("open", "high", "low", "close"))
    tod = idx.time; day = idx.normalize()
    # session "day" for Asia setups = the calendar day the session ends on
    for d, pos in pd.Series(np.arange(len(idx)), index=idx).groupby(day):
        p = pos.to_numpy()
        if setup in ("NY1", "NY2", "NY3"):
            sl = p[(tod[p] >= T("09:30")) & (tod[p] <= T("15:59"))]
            if len(sl) < 300: continue
            t = tod[sl]
            if setup in ("NY1", "NY2"):
                end_or, flat, rr = (T("09:45"), T("11:30"), 2.0) if setup == "NY1" else (T("10:00"), T("12:00"), 1.0)
                orr = sl[t < end_or]; after = sl[(t >= end_or) & (t < flat)]
                if len(orr) < 10 or len(after) < 5: continue
                hi, lo = h[orr].max(), l[orr].min(); last = after[-1]
                for k in range(len(after) - 1):
                    i = after[k]
                    if c[i] > hi or c[i] < lo:
                        side = 1 if c[i] > hi else -1; i0 = after[k + 1]; e = o[i0]
                        stop = lo if side > 0 else hi; risk = abs(e - stop)
                        if risk <= 0 or (side > 0 and e <= stop) or (side < 0 and e >= stop): break
                        tgt = e + side * rr * risk
                        x, j = trade_path(o, h, l, c, i0, side, stop, tgt, last)
                        out.append((d, side, e, x, risk)); break
            else:
                a = sl[t <= T("10:30")]
                rest = sl[t > T("10:30")]
                if len(a) < 30 or len(rest) < 10: continue
                mv = c[a[-1]] / o[a[0]] - 1
                if abs(mv) < 0.003: continue
                side = 1 if mv > 0 else -1; i0 = rest[0]; e = o[i0]
                stop = e * (1 - side * 0.004); tgt = e * (1 + side * 0.008)
                x, j = trade_path(o, h, l, c, i0, side, stop, tgt, rest[-1])
                out.append((d, side, e, x, abs(e - stop)))
    return out


def asia_trades(bars, setup):
    """Asia setups need bars spanning midnight: build an 'Asia day' key = session end date."""
    out = []
    idx = bars.index; o, h, l, c = (bars[k].to_numpy() for k in ("open", "high", "low", "close"))
    shifted = (idx + pd.Timedelta(hours=6)).normalize()        # 18:00 previous day .. 17:59 -> same key
    tod = idx.time
    for d, pos in pd.Series(np.arange(len(idx)), index=idx).groupby(shifted):
        p = pos.to_numpy(); t = tod[p]
        if setup == "AS1":
            rng_ = p[(t >= T("19:00")) | (t < T("02:00"))]
            rng_ = rng_[np.isin(rng_, p[(idx[p] < d + pd.Timedelta(hours=2))])]
            brk = p[(t >= T("02:00")) & (t < T("05:00")) & (idx[p] >= d)]
            flat = p[(t >= T("02:00")) & (t < T("08:00")) & (idx[p] >= d)]
            if len(rng_) < 200 or len(brk) < 30 or len(flat) < 60: continue
            hi, lo = h[rng_].max(), l[rng_].min(); mid = (hi + lo) / 2
            for k in range(len(brk) - 1):
                i = brk[k]
                if c[i] > hi or c[i] < lo:
                    side = 1 if c[i] > hi else -1; i0 = brk[k + 1]; e = o[i0]; risk = abs(e - mid)
                    if risk <= 0: break
                    x, j = trade_path(o, h, l, c, i0, side, mid, e + side * risk, flat[-1])
                    out.append((d, side, e, x, risk)); break
        else:   # AS2
            start = p[t == T("18:00")] if (t == T("18:00")).any() else p[(t >= T("18:00")) & (t < T("19:00"))][:1]
            if len(start) == 0: continue
            op = o[start[0]]
            win = p[((t >= T("20:00")) | (t < T("01:00"))) & (idx[p] < d + pd.Timedelta(hours=1))]
            flat = p[(idx[p] < d + pd.Timedelta(hours=2))]
            flat = flat[flat >= (win[0] if len(win) else 0)]
            if len(win) < 100 or len(flat) < 10: continue
            for k in range(len(win) - 1):
                i = win[k]; dev = c[i] / op - 1
                if abs(dev) >= 0.003:
                    side = -1 if dev > 0 else 1; i0 = win[k + 1]; e = o[i0]
                    dist = abs(e - op); stop = e - side * 1.5 * dist
                    x, j = trade_path(o, h, l, c, i0, side, stop, op, flat[-1])
                    out.append((d, side, e, x, 1.5 * dist)); break
    return out


def to_dollars(trades, pt, slip):
    rows = []
    for d, side, e, x, risk in trades:
        n = int(min(MAXC, max(1, math.floor(RISK / max(risk * pt, 1e-9)))))
        pnl = n * (side * (x - e) - slip) * pt - n * COMM
        rows.append(dict(day=pd.Timestamp(d), n=n, pnl=pnl, r=(side * (x - e) - slip) / risk))
    return pd.DataFrame(rows)


def prop(daily: pd.Series, a, b):
    """Start an evaluation every Monday in [a, b); returns pass rate, mean days to pass, EV per attempt."""
    days = daily.index; res = []
    for s in [d for d in days if a <= d < b and d.weekday() == 0]:
        seq = daily[daily.index >= s].iloc[:60]
        bal, peak, status, n = 0.0, 0.0, "timeout", 0
        for v in seq:
            n += 1; bal += v
            if v <= -1000: status = "fail"; break
            if bal >= 3000: status = "pass"; break
            peak = max(peak, bal)
            if bal <= min(peak - 2000, 0.0): status = "fail"; break
        funded = 0.0
        if status == "pass":
            nxt = daily[daily.index > seq.index[n - 1]].iloc[:21]
            fb, fpk, alive = 0.0, 0.0, True
            for v in nxt:
                fb += v; fpk = max(fpk, fb)
                if v <= -1000 or fb <= min(fpk - 2000, 0.0): alive = False; break
            funded = max(fb, 0.0) * 0.9 if alive else 0.0
        res.append((status, n, funded))
    if not res: return dict(attempts=0)
    r = pd.DataFrame(res, columns=["status", "days", "funded"])
    pr = (r.status == "pass").mean()
    return dict(attempts=len(r), pass_rate=pr, days_to_pass=r[r.status == "pass"].days.mean(),
                ev=r.funded.mean() - 150.0)


def main():
    out = ["# Round 52: NY and Asia session setups on S&P / Nasdaq micros, scored as a $50k prop-firm account", "",
           "Rules: [PROTOCOL_ROUND52.md](../PROTOCOL_ROUND52.md). HistData 1-minute index CFD bars, New York time.", ""]
    rows = []
    for name, cfg in INSTR.items():
        try:
            bars = load_nq(pair=cfg["pair"])
        except FileNotFoundError as e:
            out.append(f"{name}: no data ({e})"); continue
        print(name, bars.index.min(), bars.index.max(), len(bars), flush=True)
        for setup in ("NY1", "NY2", "NY3", "AS1", "AS2"):
            tr = session_trades(bars, setup) if setup.startswith("NY") else asia_trades(bars, setup)
            T_ = to_dollars(tr, cfg["pt"], cfg["slip"])
            if T_.empty: continue
            daily = T_.groupby("day").pnl.sum()
            alldays = pd.Index(sorted(set(bars.index.normalize())))
            daily = daily.reindex(alldays, fill_value=0.0)
            for per, a, b in (("dev", pd.Timestamp("2012-01-01"), SPLIT), ("holdout", SPLIT, pd.Timestamp("2030-01-01"))):
                x = T_[(T_.day >= a) & (T_.day < b)]
                if x.empty: continue
                t = x.r.mean() / x.r.std() * math.sqrt(len(x)) if x.r.std() > 0 else np.nan
                pr = prop(daily, a, b)
                rows.append(dict(market=name, setup=setup, period=per, trades=len(x), win=f"{(x.pnl > 0).mean():.0%}",
                                 avg_R=round(x.r.mean(), 3), t=round(t, 2), pnl_per_trade=round(x.pnl.mean(), 1),
                                 per_month=round(x.pnl.sum() / max((x.day.max() - x.day.min()).days / 30.4, 1), 0),
                                 prop_pass=f"{pr.get('pass_rate', np.nan):.0%}", days_to_pass=round(pr.get("days_to_pass", np.nan) or 0, 1),
                                 ev_per_attempt=round(pr.get("ev", np.nan), 0)))
                print(rows[-1], flush=True)
    R = pd.DataFrame(rows)
    if len(R):
        ho = R[R.period == "holdout"]
        passed = ho[(ho.t >= 2) & (ho.avg_R > 0) & (ho.prop_pass.str.rstrip("%").astype(float) >= 50) & (ho.ev_per_attempt > 0)]
        out += [R.to_markdown(index=False), "", f"**Passing (holdout): {', '.join(passed.market + ' ' + passed.setup) or 'none'}.**"]
    open("reports/ROUND52.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    main()
