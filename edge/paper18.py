"""Live paper test of Round 18 (PROTOCOL_ROUND18.md, "Forward test").

Every run (about every 10 minutes):
  1. For each US daily-high series, read today's station reports and find markets
     newly decided by the Round 15 rule (reading + 10 min must be in the past).
  2. "Place" a paper bid for the decided side at 99c for ORDER contracts, and record
     the live order-book queue already resting at >= 99c on that side (ahead of us).
  3. For open orders, count later public trades where a taker bought the losing side at
     <= 1c. We are filled only after the whole queue ahead is used up (cancels ignored,
     which is conservative).
  4. Settle filled contracts on Kalshi's official result: +1c each (minus maker fee) or
     -99c each if the call was wrong.
paper/r18_orders.csv is append-only for new orders; later runs only update fill and
settlement columns.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round15 as r15
from edge import round19 as r19
from edge import weather as wx

ROOT = Path(__file__).resolve().parent.parent / "paper"
ROOT.mkdir(exist_ok=True)
ORDERS = ROOT / "r18_orders.csv"
BID = 0.99
ORDER = 1000  # contracts per decided market (about $990 at risk)
# Round 19's holdout-eligible series (reports/ROUND19.md), frozen
R19_SERIES = ["KXLOWTNYC", "KXLOWTDEN", "KXHIGHTDAL", "KXLOWTMIA", "KXHIGHTSEA", "KXLOWTAUS", "KXHIGHTLV",
              "KXLOWTCHI", "KXLOWTOKC", "KXLOWTNOLA", "KXLOWTDAL", "KXLOWTLAX", "KXLOWTATL", "KXHIGHTSATX",
              "KXLOWTSEA", "KXLOWTSATX", "KXLOWTSFO", "KXLOWTDC", "KXLOWTBOS", "KXLOWTLV", "KXLOWTPHIL", "KXLOWTMIN"]
COLS = ["round", "ticker", "series", "city", "date", "side", "known_utc", "placed_utc", "queue_ahead", "eligible_seen",
        "fillable", "filled", "status", "result", "pnl", "settled_utc"]


def orders() -> pd.DataFrame:
    if ORDERS.exists():
        d = pd.read_csv(ORDERS, dtype={"status": str, "result": str, "settled_utc": str})
        for c in ("result", "settled_utc"):
            d[c] = d[c].fillna("")
        if "round" not in d:
            d.insert(0, "round", 18)
        return d
    return pd.DataFrame(columns=COLS)


def _event_ticker(series: str, day: pd.Timestamp) -> str:
    return f"{series}-{day:%y}{day.strftime('%b').upper()}{day:%d}"


def queue_ahead(ticker: str, side: str) -> float:
    r = wx._get(f"{wx.KALSHI}/markets/{ticker}/orderbook")
    if r is None or r.status_code != 200:
        return np.nan
    book = r.json().get("orderbook_fp") or r.json().get("orderbook") or {}
    levels = book.get(f"{side}_dollars") or []
    return float(sum(float(sz) for px, sz in levels if float(px) >= BID - 1e-9))


def eligible_volume(ticker: str, side: str, since: pd.Timestamp) -> float:
    """Contracts traded since `since` where a taker bought the losing side at <= 1c."""
    tr = r15.trades(ticker)
    if tr.empty:
        return 0.0
    loser = "no" if side == "yes" else "yes"
    hit = tr[(tr["time"] > since) & (tr["taker_side"] == loser) & (tr[f"{side}_price"] >= BID - 1e-9)]
    return float(hit["count"].sum())


def specs() -> list[tuple]:
    """(round, series, city, station, tz, kind) for every series the forward test bids on."""
    out = [(18, sr, city, r15.STATIONS[city], tz, "high") for sr, city, tier, lat, lon, tz in wx.daily_high_series()
           if city in r15.STATIONS]
    for sr in R19_SERIES:
        code, station, tz, kind = r19.resolve(sr)
        out.append((19, sr, code, station, tz, kind))
    return out


def scan_new(now: pd.Timestamp, led: pd.DataFrame) -> list[dict]:
    new, have = [], set(led["ticker"])
    for rnd, series, city, station, tz, kind in specs():
        local = now.tz_convert(tz)
        std = r15.climate_day(pd.Timestamp(local.date()), tz)
        day = pd.Timestamp(local.date()) if now >= std[0] else pd.Timestamp(local.date()) - pd.Timedelta(days=1)
        a, b = r15.climate_day(day, tz)
        r = wx._get(f"{wx.KALSHI}/markets", {"series_ticker": series, "status": "open", "limit": 1000})
        ms = r.json().get("markets", []) if r is not None and r.status_code == 200 else []
        ms = [m for m in ms if m.get("event_ticker") == _event_ticker(series, day)]
        todo = [m for m in ms if m["ticker"] not in have]
        if not todo:
            print(f"  {series} {day:%Y-%m-%d}: {len(ms)} open markets, none new", flush=True)
            continue
        obs = r15.observations(station, a - pd.Timedelta(hours=1), b)
        obs = obs[(obs.index >= a) & (obs.index < b)]
        print(f"  {series} {day:%Y-%m-%d}: {len(ms)} open markets, running {kind} "
              f"{(obs.max() if kind == 'high' else obs.min()) if len(obs) else float('nan')} from {len(obs)} reports",
              flush=True)
        ms = todo
        for m in ms:
            dec = r15.decided(m, obs, kind)
            if dec is None or dec[1] > now:
                continue
            side, known = dec
            new.append(dict(round=rnd, ticker=m["ticker"], series=series, city=city, date=day.date().isoformat(), side=side,
                            known_utc=known.isoformat(), placed_utc=now.isoformat(),
                            queue_ahead=queue_ahead(m["ticker"], side), eligible_seen=0.0, fillable=0.0, filled=0.0,
                            status="open", result="", pnl=np.nan, settled_utc=""))
    return new


def update(led: pd.DataFrame, now: pd.Timestamp) -> pd.DataFrame:
    for i in led.index[led["status"] == "open"]:
        t, side = led.at[i, "ticker"], led.at[i, "side"]
        placed = pd.Timestamp(led.at[i, "placed_utc"])
        seen = eligible_volume(t, side, placed)
        q = led.at[i, "queue_ahead"]
        q = float(q) if pd.notna(q) else 0.0
        led.at[i, "eligible_seen"] = seen
        led.at[i, "fillable"] = float(max(0.0, seen - q))
        led.at[i, "filled"] = float(min(ORDER, led.at[i, "fillable"]))
        r = wx._get(f"{wx.KALSHI}/markets/{t}")
        m = r.json().get("market", {}) if r is not None and r.status_code == 200 else {}
        if m.get("result") in ("yes", "no"):
            n = float(led.at[i, "filled"])
            right = m["result"] == side
            fee = r15._maker_fee(n, BID) if n > 0 else 0.0
            led.at[i, "result"] = m["result"]
            led.at[i, "pnl"] = round(n * ((1.0 if right else 0.0) - BID) - fee, 2)
            led.at[i, "status"] = "won" if right else "lost"
            led.at[i, "settled_utc"] = now.isoformat()
    return led


def summary(led: pd.DataFrame, now: pd.Timestamp) -> str:
    s = led[led["status"].isin(["won", "lost"])].copy()
    lines = ["# Round 18 live paper test: resting 99c bids on decided Kalshi weather outcomes", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: [PROTOCOL_ROUND18.md](../PROTOCOL_ROUND18.md), "
             f"\"Forward test\". {ORDER} contracts bid per decided market; fills only after the live queue ahead.", "",
             "| | |", "|---|---|",
             f"| Decided markets bid | {len(led)} (open {int((led['status'] == 'open').sum())}) |",
             f"| Settled | {len(s)} (wrong calls: {int((s['status'] == 'lost').sum())}) |",
             f"| Contracts filled (settled) | {s['filled'].astype(float).sum():,.0f} "
             f"(uncapped: {s['fillable'].astype(float).sum():,.0f}) |",
             f"| **Paper profit** | **${s['pnl'].astype(float).sum():+,.2f}** |",
             f"| Median queue ahead at placement | {pd.to_numeric(led['queue_ahead'], errors='coerce').median():,.0f} contracts |",
             f"| Orders that got any fill | {(led['filled'].astype(float) > 0).mean():.0%} |" if len(led) else "| Orders that got any fill | n/a |",
             ""]
    for rnd in (18, 19):
        g = s[s["round"].astype(int) == rnd]
        lines.insert(-1, f"| Round {rnd} paper profit | ${g['pnl'].astype(float).sum():+,.2f} on {len(g)} settled "
                         f"({int((g['status'] == 'lost').sum())} wrong) |")
    if len(s):
        daily = s.groupby("date")["pnl"].sum()
        cap = (s["filled"].astype(float) * BID).groupby(s["date"]).sum()
        lines += [f"Green days: {(daily > 0).sum()} of {len(daily)}; average ${daily.mean():+.2f} a day; "
                  f"peak capital filled in one day ${cap.max():,.0f}", "",
                  "| Date | Markets | Filled | P&L |", "|---|---:|---:|---:|"]
        for d, g in s.groupby("date"):
            lines.append(f"| {d} | {len(g)} | {g['filled'].astype(float).sum():,.0f} | ${g['pnl'].astype(float).sum():+.2f} |")
    return "\n".join(lines) + "\n"


def run(now: pd.Timestamp | None = None):
    now = now or pd.Timestamp.now(tz="UTC")
    led = orders()
    new = scan_new(now, led)
    if new:
        led = pd.concat([led, pd.DataFrame(new)[COLS]], ignore_index=True) if len(led) else pd.DataFrame(new)[COLS]
    led = update(led, now)
    led[COLS].to_csv(ORDERS, index=False)
    (ROOT / "ROUND18_PAPER.md").write_text(summary(led, now))
    print(f"new orders {len(new)}; open {int((led['status'] == 'open').sum())}; settled "
          f"{int(led['status'].isin(['won', 'lost']).sum())}")


if __name__ == "__main__":
    run()
