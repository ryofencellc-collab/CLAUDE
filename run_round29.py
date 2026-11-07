"""Round 29 (PROTOCOL_ROUND29.md): crypto big-move reversal, intraday momentum, overnight drift.
python run_round29.py crypto | nq | overnight | report"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from edge import stats

OUT, PART = Path("reports/ROUND29.md"), Path("reports/round29_parts")
COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
CRYPTO_COST, NQ_COST, ETF_COST = 0.0014, 1.25, 0.0002


def sharpe(d: pd.Series, per_year: int) -> float:
    d = d.dropna()
    return float(d.mean() / d.std() * math.sqrt(per_year)) if len(d) > 2 and d.std() > 0 else 0.0


def maxdd(d: pd.Series) -> float:
    eq = (1 + d.fillna(0)).cumprod()
    return float((eq / eq.cummax() - 1).min()) if len(eq) else 0.0


def summarize(d: pd.Series, per_year: int, n_trades: int) -> dict:
    return {"days": int(d.notna().sum()), "trades": int(n_trades), "total": float((1 + d.fillna(0)).prod() - 1),
            "per_day_on_1000": float(d.mean() * 1000), "sharpe": sharpe(d, per_year), "max_dd": maxdd(d)}


# ------------------------------------------------------------------ 1. crypto reversal
def reversal_trades(c: pd.Series, H: int, k: float) -> pd.Series:
    """c: hourly closes. Returns net trade returns indexed by exit time."""
    r = np.log(c).diff(H)
    sd = r.rolling(24 * 30, min_periods=24 * 20).std().shift(1)   # sigma known before the bar
    out, i, n = {}, 0, len(c)
    vals, rr, ss, idx = c.to_numpy(), r.to_numpy(), sd.to_numpy(), c.index
    while i < n - H:
        if np.isfinite(rr[i]) and np.isfinite(ss[i]) and ss[i] > 0 and abs(rr[i]) > k * ss[i]:
            side = -np.sign(rr[i])
            ret = side * (vals[i + H] / vals[i] - 1) - CRYPTO_COST
            out[idx[i + H]] = ret
            i += H
        else:
            i += 1
    return pd.Series(out, dtype=float)


def part_crypto():
    from edge import round21
    a, b = pd.Timestamp("2023-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
    closes = {}
    for s in COINS:
        m = round21.minutes(s, a, b)
        closes[s] = m.resample("1h").last().dropna()
        print(s, len(m), "minutes", flush=True)
    rows, daily_by = [], {}
    for H in (1, 2, 4):
        for k in (2, 3, 4):
            per_coin = []
            n = 0
            for s, c in closes.items():
                t = reversal_trades(c, H, k)
                n += len(t)
                if len(t):
                    t.index = pd.DatetimeIndex(t.index)
                    per_coin.append(t.groupby(t.index.floor("D")).sum())
            if not per_coin:
                per_coin = [pd.Series(0.0, index=pd.DatetimeIndex([c.index[0].floor("D")]))]
            day = pd.concat(per_coin, axis=1).fillna(0).mean(axis=1)   # capital split equally
            full = pd.date_range(day.index.min(), day.index.max(), freq="D", tz="UTC")
            day = day.reindex(full, fill_value=0.0)
            daily_by[f"H{H}_k{k}"] = day
            rows.append((f"H{H}_k{k}", n))
    save("crypto", daily_by, dict(rows), 365, (pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")),
         (pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")))


# ------------------------------------------------------------------ 2. intraday momentum (NQ)
def part_nq():
    from edge import intraday as it
    bars = it.load_nq()
    c = bars["close"]
    day = c.index.normalize()
    close16 = c[(c.index.hour == 15) & (c.index.minute == 59)].groupby(lambda t: t.normalize()).last()
    at10 = c[(c.index.hour == 9) & (c.index.minute == 59)].groupby(lambda t: t.normalize()).last()
    at1530 = c[(c.index.hour == 15) & (c.index.minute == 29)].groupby(lambda t: t.normalize()).last()
    df = pd.DataFrame({"c16": close16, "a10": at10, "a1530": at1530}).dropna()
    df["prev16"] = df["c16"].shift(1)
    df = df.dropna()
    df["sig"] = df["a10"] / df["prev16"] - 1
    df["last"] = df["c16"] - df["a1530"]
    daily_by, trades = {}, {}
    for q in (0.0, 0.5, 0.8):
        thr = df["sig"].abs().rolling(250, min_periods=120).quantile(q).shift(1) if q > 0 else pd.Series(0.0, index=df.index)
        take = df["sig"].abs() > thr
        pnl_pts = np.sign(df["sig"]) * df["last"] - NQ_COST
        ret = (pnl_pts / df["a1530"]).where(take, 0.0)
        ret.index = pd.to_datetime(ret.index).tz_localize("UTC")
        daily_by[f"q{q}"] = ret
        trades[f"q{q}"] = int(take.sum())
    save("nq", daily_by, trades, 252, (pd.Timestamp("2012-01-01", tz="UTC"), pd.Timestamp("2020-01-01", tz="UTC")),
         (pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2026-12-31", tz="UTC")))


# ------------------------------------------------------------------ 3. overnight drift
def part_overnight():
    from edge import data
    p = data.etf_panel(refresh=True)
    daily_by, trades = {}, {}
    for t in ("SPY", "QQQ", "IWM"):
        o, c = p["open"][t].dropna(), p["close"][t].dropna()
        df = pd.DataFrame({"o": o, "c": c}).dropna()
        night = df["o"].shift(-1) / df["c"] - 1 - ETF_COST              # hold from today's close to next open
        day_ret = df["c"] / df["c"].shift(1) - 1
        for name, cond in (("all", pd.Series(True, index=df.index)), ("after_up", day_ret > 0), ("after_down", day_ret < 0)):
            r = night.where(cond, 0.0).dropna()
            r.index = pd.to_datetime(r.index).tz_localize("UTC") if r.index.tz is None else r.index
            daily_by[f"{t}_{name}"] = r
            trades[f"{t}_{name}"] = int(cond.sum())
    save("overnight", daily_by, trades, 252, (pd.Timestamp("2000-01-01", tz="UTC"), pd.Timestamp("2016-01-01", tz="UTC")),
         (pd.Timestamp("2016-01-01", tz="UTC"), pd.Timestamp("2026-12-31", tz="UTC")))


def save(name, daily_by, trades, per_year, dev, hold):
    PART.mkdir(parents=True, exist_ok=True)
    rows = []
    for cfg, d in daily_by.items():
        dd = d[(d.index >= dev[0]) & (d.index < dev[1])]
        hd = d[(d.index >= hold[0]) & (d.index < hold[1])]
        rows.append({"config": cfg, "dev": summarize(dd, per_year, trades[cfg]), "hold": summarize(hd, per_year, trades[cfg])})
    best = max(rows, key=lambda r: r["dev"]["sharpe"])
    srs = [r["dev"]["sharpe"] / math.sqrt(per_year) for r in rows]
    hd = daily_by[best["config"]]
    hd = hd[(hd.index >= hold[0]) & (hd.index < hold[1])].dropna()
    dsr = stats.deflated_sharpe(hd, len(rows), float(np.var(srs))) if len(hd) > 30 else float("nan")
    json.dump({"family": name, "per_year": per_year, "dev": [str(x.date()) for x in dev], "hold": [str(x.date()) for x in hold],
               "rows": rows, "best": best["config"], "dsr": dsr}, open(PART / f"{name}.json", "w"), indent=1)
    print(json.dumps({"best": best, "dsr": dsr}, indent=1), flush=True)


def report():
    lines = ["# Round 29: three documented stock/crypto effects, tested for daily income", "",
             "Rules: [PROTOCOL_ROUND29.md](../PROTOCOL_ROUND29.md). All numbers after costs.", ""]
    titles = {"crypto": "1. Crypto big-move reversal", "nq": "2. Intraday momentum (Nasdaq-100)", "overnight": "3. Overnight drift"}
    for name in ("crypto", "nq", "overnight"):
        p = PART / f"{name}.json"
        if not p.exists():
            lines += [f"## {titles[name]}", "", "no result (data step failed)", ""]
            continue
        j = json.loads(p.read_text())
        tab = pd.DataFrame([{"config": r["config"], "dev Sharpe": round(r["dev"]["sharpe"], 2), "dev total": f"{r['dev']['total']:.1%}",
                             "hold Sharpe": round(r["hold"]["sharpe"], 2), "hold total": f"{r['hold']['total']:.1%}",
                             "hold $/day on $1k": round(r["hold"]["per_day_on_1000"], 2), "hold max DD": f"{r['hold']['max_dd']:.0%}"}
                            for r in j["rows"]])
        b = next(r for r in j["rows"] if r["config"] == j["best"])["hold"]
        checks = {"net > 0": b["total"] > 0, "Sharpe >= 1": b["sharpe"] >= 1, "max DD > -30%": b["max_dd"] > -0.30,
                  "deflated Sharpe >= 0.95": (j["dsr"] or 0) >= 0.95}
        lev = 100 / b["per_day_on_1000"] if b["per_day_on_1000"] > 0 else float("inf")
        lines += [f"## {titles[name]}", "", f"Dev {j['dev'][0]}..{j['dev'][1]}, holdout {j['hold'][0]}..{j['hold'][1]}. "
                  f"Chosen on dev: **{j['best']}**.", "",
                  f"**Verdict: {'PASS' if all(checks.values()) else 'FAIL'}** — " + ", ".join(f"{k}: {'yes' if v else 'no'}" for k, v in checks.items()), "",
                  f"Holdout: {b['total']:.1%} total, Sharpe {b['sharpe']:.2f}, worst drop {b['max_dd']:.0%}, "
                  f"**${b['per_day_on_1000']:.2f}/day on $1,000**; " + (
                      f"$100/day would need {lev:,.0f}x exposure, where its worst drop ({b['max_dd']:.0%}) becomes "
                      f"{'a total wipe-out' if b['max_dd'] * lev <= -1 else format(b['max_dd'] * lev, '.0%')}"
                      if b["per_day_on_1000"] > 0 else "it does not make money, so no leverage helps"), "",
                  tab.to_markdown(index=False), ""]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    {"crypto": part_crypto, "nq": part_nq, "overnight": part_overnight, "report": report}[sys.argv[1]]()
