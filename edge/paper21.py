"""Live paper test of Round 21 (PROTOCOL_ROUND21.md, "Forward test").

Runs a loop for RUN_SECONDS. Each pass (about every 15 s):
  1. For each series, list open markets closing within the hour.
  2. Coinbase spot from the last completed minute, and the trailing 60-minute volatility, give z for each market.
  3. z >= Z for one side and no order yet: paper-bid ORDER contracts at 99c on that side; record the queue
     already resting at >= 99c on that side.
  4. Open orders: if z falls below Z the bid is cancelled (no fills counted after that). Every ~30 s, later public
     trades where a taker bought the other side at <= 2c are counted; we are filled only after the queue ahead.
  5. After close, settle on Kalshi's result.
The ledger paper/r21_orders.csv is committed every COMMIT_EVERY seconds and at the end.
"""
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from edge import round15 as r15
from edge import weather as wx

ROOT = Path(__file__).resolve().parent.parent / "paper"
ROOT.mkdir(exist_ok=True)
ORDERS = ROOT / "r21_orders.csv"
Z, BID, ORDER = 6.0, 0.99, 1000.0
SERIES = {"KXBTC15M": "BTC-USD", "KXETH15M": "ETH-USD", "KXSOL15M": "SOL-USD", "KXXRP15M": "XRP-USD",
          "KXDOGE15M": "DOGE-USD", "KXBTCD": "BTC-USD", "KXETHD": "ETH-USD", "KXSOLD": "SOL-USD", "KXXRPD": "XRP-USD"}
# KXBNB15M is in the backtest, but BNB has no Coinbase market, so it is left out here.
RUN_SECONDS = int(os.environ.get("P21_SECONDS", 20700))
COMMIT_EVERY = 1800
COLS = ["ticker", "series", "side", "strike", "close_utc", "placed_utc", "z_at_place", "spot_at_place", "queue_ahead",
        "seen", "filled", "status", "cancelled_utc", "result", "pnl", "settled_utc"]
CB = "https://api.exchange.coinbase.com/products/{}/candles"
_cb = requests.Session()


def ledger() -> pd.DataFrame:
    if ORDERS.exists():
        d = pd.read_csv(ORDERS, dtype={"status": str, "result": str, "settled_utc": str, "cancelled_utc": str})
        for c in ("result", "settled_utc", "cancelled_utc"):
            d[c] = d[c].fillna("")
        return d
    return pd.DataFrame(columns=COLS)


def spot_and_vol(product: str, now: pd.Timestamp):
    """(close of the last completed minute, per-minute vol over the trailing 60) from Coinbase 1-minute candles."""
    try:
        r = _cb.get(CB.format(product), params={"granularity": 60}, timeout=20, headers={"User-Agent": "paper21"})
        rows = r.json() if r.status_code == 200 else []
    except (requests.RequestException, ValueError):
        rows = []
    if not rows:
        return np.nan, np.nan
    c = pd.Series({pd.Timestamp(x[0] + 60, unit="s", tz="UTC"): float(x[4]) for x in rows}).sort_index()
    c = c[c.index <= now]
    vol = np.log(c).diff().tail(60).std()
    return (float(c.iloc[-1]) if len(c) else np.nan), float(vol)


def z_for(spot, vol, strike, close, now):
    tau = max((close - now).total_seconds() / 60, 0.5)
    return np.log(spot / strike) / (vol * np.sqrt(tau)) if vol and vol > 0 else np.nan


def queue_ahead(ticker: str, side: str) -> float:
    r = wx._get(f"{wx.KALSHI}/markets/{ticker}/orderbook")
    if r is None or r.status_code != 200:
        return np.nan
    book = r.json().get("orderbook_fp") or r.json().get("orderbook") or {}
    return float(sum(float(sz) for px, sz in (book.get(f"{side}_dollars") or []) if float(px) >= BID - 1e-9))


def seen_since(ticker: str, side: str, since: pd.Timestamp, until: pd.Timestamp) -> float:
    other = "no" if side == "yes" else "yes"
    n, cursor = 0.0, None
    for _ in range(20):
        p = {"ticker": ticker, "limit": 1000, "min_ts": int(since.timestamp())}
        if cursor:
            p["cursor"] = cursor
        r = wx._get(f"{wx.KALSHI}/markets/trades", p)
        if r is None or r.status_code != 200:
            break
        j = r.json()
        for t in j.get("trades", []):
            ts = pd.Timestamp(t["created_time"])
            px = float(t.get(f"{other}_price_dollars") or 1)
            if t.get("taker_side") == other and px <= 0.02 + 1e-9 and since < ts <= until:
                n += float(t.get("count_fp") or t.get("count") or 0)
        cursor = j.get("cursor")
        if not cursor or not j.get("trades"):
            break
    return n


def open_markets(series: str, now: pd.Timestamp) -> list[dict]:
    r = wx._get(f"{wx.KALSHI}/markets", {"series_ticker": series, "status": "open", "limit": 1000})
    ms = r.json().get("markets", []) if r is not None and r.status_code == 200 else []
    out = []
    for m in ms:
        close = pd.to_datetime(m.get("close_time"), utc=True, errors="coerce")
        if m.get("strike_type") in ("greater", "greater_or_equal") and pd.notna(close) and \
                now + pd.Timedelta(seconds=5) < close <= now + pd.Timedelta(hours=1):
            out.append({**m, "_close": close})
    return out


def place(led: pd.DataFrame, now: pd.Timestamp) -> pd.DataFrame:
    have, new = set(led["ticker"]), []
    spots = {p: spot_and_vol(p, now) for p in set(SERIES.values())}
    for series, product in SERIES.items():
        s, v = spots[product]
        if not np.isfinite(s):
            continue
        for m in open_markets(series, now):
            z = z_for(s, v, float(m["floor_strike"]), m["_close"], now)
            if m["ticker"] in have or not np.isfinite(z) or abs(z) < Z:
                continue
            side = "yes" if z > 0 else "no"
            new.append(dict(ticker=m["ticker"], series=series, side=side, strike=m["floor_strike"],
                            close_utc=m["_close"].isoformat(), placed_utc=now.isoformat(), z_at_place=round(abs(z), 2),
                            spot_at_place=s, queue_ahead=queue_ahead(m["ticker"], side), seen=0.0, filled=0.0,
                            status="open", cancelled_utc="", result="", pnl=np.nan, settled_utc=""))
    if new:
        print(f"{now:%H:%M:%S} placed {len(new)}: {[x['ticker'] for x in new][:6]}", flush=True)
        led = pd.concat([led, pd.DataFrame(new)[COLS]], ignore_index=True) if len(led) else pd.DataFrame(new)[COLS]
    return led


def watch(led: pd.DataFrame, now: pd.Timestamp, count_fills: bool) -> pd.DataFrame:
    spots = {}
    for i in led.index[led["status"].isin(["open", "cancelled"])]:
        close = pd.Timestamp(led.at[i, "close_utc"])
        side = led.at[i, "side"]
        if led.at[i, "status"] == "open" and now < close:
            prod = SERIES[led.at[i, "series"]]
            spots.setdefault(prod, spot_and_vol(prod, now))
            s, v = spots[prod]
            z = z_for(s, v, float(led.at[i, "strike"]), close, now)
            if np.isfinite(z) and (z if side == "yes" else -z) < Z:
                led.at[i, "status"], led.at[i, "cancelled_utc"] = "cancelled", now.isoformat()
        if count_fills or now >= close:
            until = pd.Timestamp(led.at[i, "cancelled_utc"]) if led.at[i, "cancelled_utc"] else min(now, close)
            seen = seen_since(led.at[i, "ticker"], side, pd.Timestamp(led.at[i, "placed_utc"]), until)
            q = led.at[i, "queue_ahead"]
            led.at[i, "seen"] = seen
            led.at[i, "filled"] = float(min(ORDER, max(0.0, seen - (float(q) if pd.notna(q) else 0.0))))
        if now >= close + pd.Timedelta(minutes=2):
            r = wx._get(f"{wx.KALSHI}/markets/{led.at[i, 'ticker']}")
            m = r.json().get("market", {}) if r is not None and r.status_code == 200 else {}
            if m.get("result") in ("yes", "no"):
                n = float(led.at[i, "filled"])
                right = m["result"] == side
                fee = r15._maker_fee(n, BID) if n > 0 else 0.0
                led.at[i, "result"], led.at[i, "settled_utc"] = m["result"], now.isoformat()
                led.at[i, "pnl"] = round(n * ((1.0 if right else 0.0) - BID) - fee, 2)
                led.at[i, "status"] = "won" if right else "lost"
    return led


def summary(led: pd.DataFrame, now: pd.Timestamp) -> str:
    s = led[led["status"].isin(["won", "lost"])].copy()
    s["day"] = pd.to_datetime(s["settled_utc"]).dt.date.astype(str) if len(s) else []
    filled = s[s["filled"].astype(float) > 0]
    lines = ["# Round 21 live paper test: 99c bids on crypto markets decided by the spot price", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: [PROTOCOL_ROUND21.md](../PROTOCOL_ROUND21.md), \"Forward test\". "
             f"{ORDER:,.0f} contracts per market at z >= {Z:g}; fills only after the live queue ahead.", "",
             "| | |", "|---|---|",
             f"| Markets bid | {len(led)} (open {int((led['status'] == 'open').sum())}, cancelled before close "
             f"{int((led['cancelled_utc'] != '').sum())}) |",
             f"| Settled | {len(s)}; with fills {len(filled)}; losing filled markets {int((filled['status'] == 'lost').sum())} |",
             f"| Contracts filled | {s['filled'].astype(float).sum():,.0f} |",
             f"| **Paper profit** | **${s['pnl'].astype(float).sum():+,.2f}** |",
             f"| Median queue ahead at placement | {pd.to_numeric(led['queue_ahead'], errors='coerce').median():,.0f} |",
             f"| Markets that got any fill | {(s['filled'].astype(float) > 0).mean() if len(s) else 0:.0%} |", ""]
    if len(s):
        lines += ["| Day | Settled | Filled | P&L |", "|---|---:|---:|---:|"]
        for d, g in s.groupby("day"):
            lines.append(f"| {d} | {len(g)} | {g['filled'].astype(float).sum():,.0f} | ${g['pnl'].astype(float).sum():+.2f} |")
        lines += ["", "| Series | Settled | Filled | P&L |", "|---|---:|---:|---:|"]
        for k, g in s.groupby("series"):
            lines.append(f"| {k} | {len(g)} | {g['filled'].astype(float).sum():,.0f} | ${g['pnl'].astype(float).sum():+.2f} |")
    return "\n".join(lines) + "\n"


def save(led, now):
    led[COLS].to_csv(ORDERS, index=False)
    (ROOT / "ROUND21_PAPER.md").write_text(summary(led, now))


def commit(now):
    cmds = [["git", "add", "paper/r21_orders.csv", "paper/ROUND21_PAPER.md"],
            ["git", "commit", "-q", "-m", f"paper21: ledger {now:%Y-%m-%dT%H:%MZ} [skip ci]"],
            ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]]
    for c in cmds:
        if subprocess.run(c, cwd=ROOT.parent).returncode != 0 and c[1] in ("commit",):
            return


def run():
    t0 = time.time()
    led, last_fill, last_commit = ledger(), 0.0, time.time()
    while time.time() - t0 < RUN_SECONDS:
        now = pd.Timestamp.now(tz="UTC")
        try:
            led = place(led, now)
            count = time.time() - last_fill > 30
            led = watch(led, now, count)
            if count:
                last_fill = time.time()
            save(led, now)
        except Exception as e:  # keep the loop alive; the ledger is saved every pass
            print(f"{now:%H:%M:%S} pass failed: {e!r}", flush=True)
        if os.environ.get("P21_COMMIT") == "1" and time.time() - last_commit > COMMIT_EVERY:
            commit(now)
            last_commit = time.time()
        time.sleep(max(0.0, 15 - (time.time() - now.timestamp())))
    now = pd.Timestamp.now(tz="UTC")
    save(led, now)
    if os.environ.get("P21_COMMIT") == "1":
        commit(now)
    print(summary(led, now))


if __name__ == "__main__":
    run()
