"""Round 26 backtest: the live trader as it now stands vs the earlier versions, on Round 21's Kalshi long-shot
fills (Apr 1 - Oct 28 2026; artifacts of run 40886253855) and the same capture assumption (25% of each trade).

Every version runs through ONE simulator that copies the live bot (edge/live21.py):
  - one market at a time; the position grows with later fills in that market, up to stake x balance / 99c;
  - a fill counts only while the bid would be resting (the version's entry/keep rule holds at that moment);
  - the governor: stake 0.5 for the first 14 days, 0.95 after 14 days with P&L >= 0 and no loss in 14 days,
    0.25 for 14 days after a loss; 24 h pause and 7 days at half size after any loss; halt for good at 70%
    of the start or 2 losses within 7 days; no new market after a 10% loss on the day;
  - maker fee per fill (Kalshi's quadratic fee).
'honest' fills keep only trades whose long-shot price is >= 1c: the only ones that can reach a 99c bid (the
15-minute markets quote 0.1c steps above 90c; reports/FILLCHECK.md). Hourly markets trade in whole cents, so
'honest' changes nothing there.

python run_round26.py            (expects data/r21/*.pkl)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round25 as r25

FILLS, OUT = Path("data/r21"), Path("reports/ROUND26_BACKTEST.md")
DEV = (pd.Timestamp("2026-04-01", tz="UTC"), pd.Timestamp("2026-09-30", tz="UTC"))
HOLD = (pd.Timestamp("2026-10-01", tz="UTC"), pd.Timestamp("2026-10-28", tz="UTC"))
K15 = ["KXBTC15M", "KXETH15M", "KXSOL15M", "KXXRP15M", "KXDOGE15M"]
HOURLY = ["KXBTCD", "KXETHD", "KXSOLD", "KXXRPD"]
PRICE, CAP_SHARE = 0.99, 0.25
P_MAX, Z_HOURLY = 0.003, 6.0


def load() -> pd.DataFrame:
    parts = []
    for s in K15 + HOURLY:
        for tag in ("dev", "hold"):
            p = FILLS / f"{s}_{tag}.pkl"
            if p.exists():
                f = pd.read_pickle(p)
                if len(f):
                    f = f.copy()
                    f["series"] = s
                    parts.append(f)
    f = pd.concat(parts, ignore_index=True)
    f["time"] = pd.to_datetime(f["time"], utc=True)
    f["close"] = (f["time"] + pd.to_timedelta(f["min_to_close"], unit="min")).dt.round("1min")
    f["ours_won"] = ~f["won_longshot"].astype(bool)
    f["weight"] = f.get("weight", 1)
    return f.sort_values("time").reset_index(drop=True)


def table_risk(az: np.ndarray, tau: np.ndarray, path=Path("control/r25_zbins.json")) -> np.ndarray:
    """Round 25 reversal table exactly as the live bot reads it (made monotone in |z|)."""
    t = json.loads(path.read_text())
    rate = np.minimum.accumulate(np.asarray(t["rate"], dtype=float), axis=0)
    zi = np.clip(np.searchsorted(t["z_edges"], az, side="left") - 1, 0, rate.shape[0] - 1)
    ti = np.clip(np.searchsorted(t["tau_edges"], tau, side="left") - 1, 0, rate.shape[1] - 1)
    return rate[zi, ti]


def kelly(p):
    return np.clip((1 - p) - p * 99, 0, None)


def simulate(f: pd.DataFrame, ok: np.ndarray, kfrac: np.ndarray, governor: bool = True, cap: float = 0.95,
             capture: float = CAP_SHARE, start: float = 1000.0) -> dict:
    """ok: the bid is resting at this fill; kfrac: the version's own size limit (1 = none)."""
    bal, peak, maxdd = start, start, 0.0
    t0 = f["time"].iloc[0] if len(f) else None
    active, held, fees = None, 0.0, 0.0
    losses, markets, halted, day, day_start, pause_until, half_until = [], 0, None, None, start, None, None
    daily = {}

    def stake(now):
        if not governor:
            return cap
        recent = [t for t in losses if now - t < pd.Timedelta(days=14)]
        if recent:
            s = 0.25
        elif now - t0 >= pd.Timedelta(days=14) and bal >= start:
            s = 0.95
        else:
            s = 0.5
        s = min(s, cap)
        return s / 2 if half_until is not None and now < half_until else s

    def settle(now):
        nonlocal bal, peak, maxdd, active, held, fees, markets, halted, pause_until, half_until
        won = active["won"]
        pnl = held * (0.01 if won else -0.99) - fees
        if held > 0:
            markets += 1
            if not won:
                losses.append(active["close"])
                pause_until = active["close"] + pd.Timedelta(hours=24)
                half_until = pause_until + pd.Timedelta(days=7)
        bal += pnl
        d = active["close"].date()
        daily[d] = daily.get(d, 0.0) + pnl
        peak = max(peak, bal)
        maxdd = min(maxdd, bal / peak - 1)
        if governor and halted is None:
            if bal <= 0.70 * start:
                halted = (active["close"], "equity floor")
            elif len(losses) >= 2 and losses[-1] - losses[-2] <= pd.Timedelta(days=7):
                halted = (active["close"], "2 losses in 7 days")
        active, held, fees = None, 0.0, 0.0

    cols = f[["time", "ticker", "close", "count", "ours_won"]].itertuples(index=False)
    for (t, ticker, close, count, won), g, kf in zip(cols, ok, kfrac):
        if active is not None and t >= active["close"]:
            settle(t)
        if halted is not None:
            break
        if day != t.date():
            day, day_start = t.date(), bal
        if active is not None and ticker != active["ticker"]:
            continue
        if not g or bal <= 1:
            continue
        if active is None:
            if governor and ((pause_until is not None and t < pause_until) or bal < day_start * 0.90):
                continue
        size = math.floor(min(stake(t), kf) * bal / PRICE)
        add = min(capture * count, max(0.0, size - held))
        if add <= 0:
            continue
        if active is None:
            active = {"ticker": ticker, "close": close, "won": won}
        held += add
        fees += r25.fee(add)
    if active is not None and halted is None:
        settle(active["close"])
    days = max((f["time"].max() - f["time"].min()).total_seconds() / 86400, 1) if len(f) else 1
    s = pd.Series(daily, dtype=float)
    return {"final": bal, "per_day": (bal - start) / days, "growth": (bal / start) ** (1 / days) - 1 if bal > 0 else -1,
            "max_dd": maxdd, "markets": markets, "losses": len(losses), "green": float((s > 0).mean()) if len(s) else 0,
            "halted": f"{halted[0]:%b %d} ({halted[1]})" if halted else "no", "days": days}


def versions(f: pd.DataFrame) -> dict:
    """name -> (rows mask, ok, kfrac, governor, cap)."""
    k15, hourly = f["series"].isin(K15).to_numpy(), f["series"].isin(HOURLY).to_numpy()
    z = f["z_for_us"].to_numpy(dtype=float)
    tau = np.maximum(f["min_to_close"].to_numpy(dtype=float), 0.5)
    honest = (f["px"].to_numpy(dtype=float) >= 0.01 - 1e-9)
    risk = np.where(z > 0, table_risk(np.abs(z), tau), 1.0)
    gate25 = (z > 0) & (risk < P_MAX)
    z6 = z >= Z_HOURLY
    one = np.ones(len(f))
    return {
        "A. Round 25 as reported (15-min, Kelly cap 0.95, no governor, all fills)":
            (k15, gate25, kelly(risk), False, 0.95),
        "B. Old live bot (15-min, Round 25 rule + governor), all fills":
            (k15, gate25, kelly(risk), True, 0.95),
        "C. Old live bot, honest fills":
            (k15 & honest, gate25, kelly(risk), True, 0.95),
        "D. 15-min, z>=6 + governor, honest fills":
            (k15 & honest, z6, one, True, 0.95),
        "E. NEW: hourly, z>=6 + governor (Round 26)":
            (hourly & honest, z6, one, True, 0.95),
        "F. hourly + 15-min (15-min on the Round 25 rule), honest":
            ((hourly | k15) & honest, np.where(hourly, z6, gate25), np.where(hourly, 1.0, kelly(risk)), True, 0.95),
    }


def run():
    f = load()
    lines = ["# Round 26 backtest: new live trader vs earlier versions", "", __doc__.split("\n\n")[1].strip(), "",
             f"Long-shot fills loaded: {len(f):,} ({', '.join(f'{s} {n:,}' for s, n in f['series'].value_counts().items())}).",
             f"Share of 15-minute long-shot volume priced under 1c (can't reach 99c): "
             f"{f[f.series.isin(K15) & (f.px < 0.01 - 1e-9)]['count'].sum() / max(f[f.series.isin(K15)]['count'].sum(), 1):.1%}; "
             f"hourly: {f[f.series.isin(HOURLY) & (f.px < 0.01 - 1e-9)]['count'].sum() / max(f[f.series.isin(HOURLY)]['count'].sum(), 1):.1%}.",
             "", "Sampling: Round 21 tested at most 1,500 markets per series per period (every k-th market), so these "
             "runs see a fraction of all markets: weights " +
             ", ".join(f"{s} 1/{int(w)}" for s, w in f.groupby("series")["weight"].max().items()) + ".", ""]
    month = f[f.series.isin(K15)].assign(m=f["time"].dt.strftime("%Y-%m"), sub=lambda x: x.px < 0.01 - 1e-9)
    by = month.groupby("m").apply(lambda x: x.loc[x["sub"], "count"].sum() / max(x["count"].sum(), 1), include_groups=False)
    lines += ["15-minute long-shot volume under 1c, by month: " + ", ".join(f"{k} {v:.0%}" for k, v in by.items()), ""]
    for capture in (0.25, 0.10, 0.50):
        for pname, (a, b) in (("Holdout Oct 1-28", HOLD), ("Dev Apr-Sep", DEV)):
            if capture != 0.25 and pname.startswith("Dev"):
                continue
            seg = f[(f["time"] >= a) & (f["time"] < b)].reset_index(drop=True)
            rows = []
            for name, (mask, ok, kf, gov, cap) in versions(seg).items():
                sub = seg[mask].reset_index(drop=True)
                res = simulate(sub, ok[mask], kf[mask], governor=gov, cap=cap, capture=capture)
                rows.append({"version": name, "$1,000 ->": f"${res['final']:,.0f}", "$/day": f"{res['per_day']:,.2f}",
                             "daily growth": f"{res['growth']:.2%}", "markets": res["markets"], "losses": res["losses"],
                             "max drawdown": f"{res['max_dd']:.0%}", "green days": f"{res['green']:.0%}",
                             "halted": res["halted"]})
            lines += [f"## {pname}, capture {capture:.0%}", "", pd.DataFrame(rows).to_markdown(index=False), ""]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    run()
