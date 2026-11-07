"""Round 28 (PROTOCOL_ROUND28.md): live queue survey of the Round 27 candidates.

The Round 27 scan showed long-shot buyers at 1-2c lose almost everywhere, but it cannot see the line of 99c
bids ahead of a newcomer (its 15-minute crypto control wrongly 'confirmed'). This paper bot measures that line
live. Every PASS_SECONDS, for each series in control/r28_series.json, it lists open markets (one call per
series; the listing carries the best bids and the size at the top level):

  join: the first time a side's best bid is >= 98c, we 'join' with a paper 99c bid on that side, behind
        everything already at 99c (queue = YES-bid size at 99c, or YES-ask size at 1c for the NO side);
  fill: after the close, every long-shot trade at 1-2c on the other side after we joined is counted; we are
        filled only after the queue ahead (FIFO), at most ORDER contracts;
  P&L:  +1c per contract if our side wins, -99c if not, minus the maker fee.

No cancel rule: this measures the simplest 'join when the price says decided' entry."""
import json
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round15 as r15
from edge import round27 as r27
from edge import weather as wx

ROOT = Path(__file__).resolve().parent.parent
LEDGER, REPORT = ROOT / "paper" / "r28_ledger.csv", ROOT / "paper" / "ROUND28_PAPER.md"
SERIES = json.loads((ROOT / "control" / "r28_series.json").read_text())["series"]
ORDER, JOIN_AT, PASS_SECONDS = 1000.0, 0.98, 60
RUN_SECONDS = int(os.environ.get("R28_SECONDS", 20700))
COLS = ["series", "ticker", "side", "close_utc", "joined_utc", "best_bid", "queue", "reach", "filled", "result", "pnl",
        "settled_utc"]


def f(x, k):
    try:
        return float(x.get(k)) if x.get(k) not in (None, "") else np.nan
    except (TypeError, ValueError):
        return np.nan


def queue_99(m: dict, side: str) -> float:
    """Size resting at 99c on `side` (whole-cent markets: 99c is the top bid)."""
    if side == "yes":
        return f(m, "yes_bid_size_fp") if abs(f(m, "yes_bid_dollars") - 0.99) < 1e-9 else 0.0
    return f(m, "yes_ask_size_fp") if abs(f(m, "yes_ask_dollars") - 0.01) < 1e-9 else 0.0


def decided_side(m: dict):
    """A side counts as decided only on a real two-sided book: its bid is 98-99c AND the other side is really
    offered at 1-2c. (A new market with an empty book lists a placeholder bid of $1.00: ignored.)"""
    yb, nb = f(m, "yes_bid_dollars"), f(m, "no_bid_dollars")
    ya = f(m, "yes_ask_dollars")
    if np.isfinite(yb) and JOIN_AT - 1e-9 <= yb <= 0.99 + 1e-9 and np.isfinite(ya) and ya <= 1.0 - 1e-9:
        return "yes", yb
    if np.isfinite(nb) and JOIN_AT - 1e-9 <= nb <= 0.99 + 1e-9 and np.isfinite(ya) and 0.01 - 1e-9 <= ya <= 0.02 + 1e-9:
        return "no", nb
    return None, np.nan


def open_markets(series: str) -> list[dict]:
    out, cursor = [], None
    for _ in range(5):
        p = {"series_ticker": series, "status": "open", "limit": 1000}
        if cursor:
            p["cursor"] = cursor
        r = wx._get(f"{wx.KALSHI}/markets", p)
        if r is None or r.status_code != 200:
            break
        j = r.json()
        out += j.get("markets", [])
        cursor = j.get("cursor")
        if not cursor or not j.get("markets"):
            break
    return out


def load() -> pd.DataFrame:
    if LEDGER.exists() and LEDGER.stat().st_size:
        d = pd.read_csv(LEDGER)
        return d[~(pd.to_numeric(d["best_bid"], errors="coerce") > 0.99 + 1e-9)].reset_index(drop=True)  # placeholder joins
    return pd.DataFrame(columns=COLS)


def join_pass(led: pd.DataFrame, now: pd.Timestamp) -> pd.DataFrame:
    have, new = set(led["ticker"]), []
    for s in SERIES:
        for m in open_markets(s):
            if m.get("ticker") in have or m.get("price_level_structure", "linear_cent") != "linear_cent":
                continue
            side, bid = decided_side(m)
            close = pd.to_datetime(m.get("close_time"), utc=True, errors="coerce")
            if side is None or pd.isna(close) or close <= now:
                continue
            new.append(dict(series=s, ticker=m["ticker"], side=side, close_utc=close.isoformat(), joined_utc=now.isoformat(),
                            best_bid=bid, queue=queue_99(m, side), reach=np.nan, filled=np.nan, result="", pnl=np.nan,
                            settled_utc=""))
    if new:
        led = pd.concat([led, pd.DataFrame(new)[COLS]], ignore_index=True) if len(led) else pd.DataFrame(new)[COLS]
    return led


def flow_after(ticker: str, side: str, since: pd.Timestamp) -> float:
    other = "no" if side == "yes" else "yes"
    n = 0.0
    for t in r27.trades(ticker, pd.Timestamp.now(tz="UTC"), pd.Timestamp("2000-01-01", tz="UTC")):
        if t.get("taker_side") != other or pd.Timestamp(t["created_time"]) <= since:
            continue
        try:
            px = float(t.get(f"{other}_price_dollars"))
        except (TypeError, ValueError):
            continue
        if 0.01 - 1e-9 <= px <= 0.02 + 1e-9:
            n += float(t.get("count_fp") or 0)
    return n


def settle_pass(led: pd.DataFrame, now: pd.Timestamp, limit: int = 40) -> pd.DataFrame:
    todo = led.index[(led["result"].fillna("") == "") & (pd.to_datetime(led["close_utc"], utc=True) < now - pd.Timedelta(minutes=3))]
    for i in todo[:limit]:
        r = wx._get(f"{wx.KALSHI}/markets/{led.at[i, 'ticker']}")
        m = r.json().get("market", {}) if r is not None and r.status_code == 200 else {}
        res = m.get("result")
        if res not in ("yes", "no"):
            if now > pd.Timestamp(led.at[i, "close_utc"]) + pd.Timedelta(days=3):
                led.at[i, "result"] = "void"
            continue
        reach = flow_after(led.at[i, "ticker"], led.at[i, "side"], pd.Timestamp(led.at[i, "joined_utc"]))
        q = float(led.at[i, "queue"]) if pd.notna(led.at[i, "queue"]) else 0.0
        n = float(min(ORDER, max(0.0, reach - q)))
        right = res == led.at[i, "side"]
        led.at[i, "reach"], led.at[i, "filled"], led.at[i, "result"] = reach, n, res
        led.at[i, "pnl"] = round(n * ((1.0 if right else 0.0) - 0.99) - (r15._maker_fee(n, 0.99) if n > 0 else 0.0), 2)
        led.at[i, "settled_utc"] = now.isoformat()
    return led


def summary(led: pd.DataFrame, now: pd.Timestamp) -> str:
    d = led[led["result"].isin(["yes", "no"])].copy()
    lines = ["# Round 28 paper: live queue survey", "", f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: "
             "[PROTOCOL_ROUND28.md](../PROTOCOL_ROUND28.md). Joined markets: "
             f"{len(led)}; settled: {len(d)}.", ""]
    if d.empty:
        return "\n".join(lines + ["Nothing settled yet."]) + "\n"
    d["won"] = d["result"] == d["side"]
    g = d.groupby("series").agg(markets=("ticker", "size"), filled=("filled", lambda x: int((x > 0).sum())),
                                contracts=("filled", "sum"), median_queue=("queue", "median"), reach=("reach", "sum"),
                                pnl=("pnl", "sum"), wrong=("won", lambda x: int((~x).sum())),
                                wrong_filled=("pnl", lambda x: int((x < -1).sum()))).sort_values("pnl", ascending=False)
    lines += [f"Total paper P&L: **${d['pnl'].sum():,.2f}**; filled markets {int((d['filled'] > 0).sum())}; "
              f"wrong calls {int((~d['won']).sum())}, of which filled {int((d['pnl'] < -1).sum())}.", "",
              g.round(2).to_markdown()]
    return "\n".join(lines) + "\n"


def commit(now):
    for c in (["git", "add", str(LEDGER.relative_to(ROOT)), str(REPORT.relative_to(ROOT))],
              ["git", "commit", "-q", "-m", f"round28: ledger {now:%Y-%m-%dT%H:%MZ} [skip ci]"],
              ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]):
        try:
            if subprocess.run(c, cwd=ROOT, timeout=120).returncode != 0 and c[1] == "commit":
                return
        except subprocess.TimeoutExpired:
            return


def run():
    LEDGER.parent.mkdir(exist_ok=True)
    led, t0, last_commit = load(), time.time(), time.time()
    while time.time() - t0 < RUN_SECONDS:
        now = pd.Timestamp.now(tz="UTC")
        try:
            led = join_pass(led, now)
            led = settle_pass(led, now)
            led.to_csv(LEDGER, index=False)
        except Exception as e:
            print(f"{now:%H:%M:%S} pass failed: {e!r}", flush=True)
        if os.environ.get("R28_COMMIT") == "1" and time.time() - last_commit > 3600:
            REPORT.write_text(summary(led, now))
            commit(now)
            last_commit = time.time()
        time.sleep(max(0.0, PASS_SECONDS - (time.time() - now.timestamp())))
    now = pd.Timestamp.now(tz="UTC")
    REPORT.write_text(summary(led, now))
    if os.environ.get("R28_COMMIT") == "1":
        commit(now)
    print(summary(led, now))


if __name__ == "__main__":
    run()
