"""Round 43: riskless-arbitrage scanner across every open Kalshi event (and Polymarket negative-risk events).

Checks, each net of taker fees at the size available at the top of the book:
  K-MONO  strike ladder ("above K"): YES ask of a lower strike < YES bid of a higher strike.
          Buy YES(K_low) + NO(K_high); every outcome pays >= $1.
  K-NOALL mutually exclusive event (at most one YES): sum of YES bids > 1. Buy NO on every market; pays >= n-1.
  K-YESALL mutually exclusive event: sum of YES asks < 1. Pays $1 only if the listed markets are exhaustive, so it is
          logged separately as *conditional*, never counted as riskless.
  P-NOALL / P-YESALL the same on Polymarket negative-risk events (fees 0 on most markets; conditional as above).
Every hit is logged with legs, size, cost, net profit, days to close and annualized return.
"""
from __future__ import annotations
import json, math, os, subprocess, time
import pandas as pd
import requests

from edge import weather as wx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "paper", "r43_arb.csv")
REPORT = os.path.join(ROOT, "paper", "ROUND43_ARB.md")
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
RUN_SECONDS = int(os.environ.get("R43_SECONDS", str(5 * 3600 + 40 * 60)))
PASS_SECONDS = int(os.environ.get("R43_PASS", "180"))
MIN_PROFIT = 0.05  # dollars: ignore sub-nickel noise


def f(x, d=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def taker_fee(n: float, p: float, mult: float = 0.07) -> float:
    """Kalshi taker fee for one order: ceil(mult * n * p * (1-p)) to the cent."""
    if n <= 0 or p <= 0 or p >= 1:
        return 0.0
    return math.ceil(mult * n * p * (1 - p) * 100 - 1e-9) / 100


def quotes(m: dict) -> dict:
    yb, ya = f(m.get("yes_bid_dollars"), 0.0), f(m.get("yes_ask_dollars"), 1.0)
    return {"ticker": m.get("ticker"), "yb": yb, "ya": ya, "ybs": f(m.get("yes_bid_size_fp"), 0.0),
            "yas": f(m.get("yes_ask_size_fp"), 0.0), "K": f(m.get("floor_strike")), "type": m.get("strike_type"),
            "close": m.get("close_time"), "status": m.get("status")}


def mono(event: str, ms: list[dict]) -> list[dict]:
    """Strike-ladder violations among 'greater' markets of one event."""
    q = sorted([quotes(m) for m in ms if m.get("strike_type") in ("greater", "greater_or_equal")
                and pd.notna(f(m.get("floor_strike")))], key=lambda x: x["K"])
    out = []
    for i, lo in enumerate(q):
        if not (0 < lo["ya"] < 1) or lo["yas"] <= 0:
            continue
        for hi in q[i + 1:]:
            if hi["K"] <= lo["K"] or not (0 < hi["yb"] < 1) or hi["ybs"] <= 0 or lo["ya"] >= hi["yb"]:
                continue
            n = math.floor(min(lo["yas"], hi["ybs"]))
            cost = n * (lo["ya"] + (1 - hi["yb"]))
            fees = taker_fee(n, lo["ya"]) + taker_fee(n, 1 - hi["yb"])
            out.append(dict(kind="K-MONO", event=event, legs=f"YES {lo['ticker']} @{lo['ya']:.3f} + NO {hi['ticker']} @{1 - hi['yb']:.3f}",
                            n=n, cost=cost, payout=n, profit=n - cost - fees, fees=fees, close=lo["close"], riskless=True))
    return out


def allsides(kind: str, event: str, ms: list[dict], fee_fn) -> list[dict]:
    q = [quotes(m) for m in ms if m.get("status") in (None, "active", "open")]
    out = []
    if len(q) < 2:
        return out
    # buy NO everywhere: pays n-1 (at most one YES); each NO costs 1 - yes_bid, size = yes bid size
    if all(0 < x["yb"] < 1 and x["ybs"] > 0 for x in q) and sum(x["yb"] for x in q) > 1:
        n = math.floor(min(x["ybs"] for x in q))
        cost = sum(n * (1 - x["yb"]) for x in q)
        fees = sum(fee_fn(n, 1 - x["yb"]) for x in q)
        out.append(dict(kind=f"{kind}-NOALL", event=event, legs=f"NO on {len(q)} markets, sum of YES bids {sum(x['yb'] for x in q):.3f}",
                        n=n, cost=cost, payout=n * (len(q) - 1), profit=n * (len(q) - 1) - cost - fees, fees=fees,
                        close=max((x["close"] or "") for x in q), riskless=True))
    if all(0 < x["ya"] < 1 and x["yas"] > 0 for x in q) and sum(x["ya"] for x in q) < 1:
        n = math.floor(min(x["yas"] for x in q))
        cost = sum(n * x["ya"] for x in q)
        fees = sum(fee_fn(n, x["ya"]) for x in q)
        out.append(dict(kind=f"{kind}-YESALL", event=event, legs=f"YES on {len(q)} markets, sum of YES asks {sum(x['ya'] for x in q):.3f}",
                        n=n, cost=cost, payout=n, profit=n - cost - fees, fees=fees,
                        close=max((x["close"] or "") for x in q), riskless=False))
    return out


def kalshi_events():
    cursor, pages = None, 0
    while pages < 300:
        pages += 1
        p = {"status": "open", "with_nested_markets": "true", "limit": 200}
        if cursor:
            p["cursor"] = cursor
        r = wx._get(f"{wx.KALSHI}/events", p)
        if r is None or r.status_code != 200:
            return
        j = r.json()
        for e in j.get("events", []):
            yield e
        cursor = j.get("cursor")
        if not cursor or not j.get("events"):
            return


def scan_kalshi() -> tuple[list[dict], int]:
    hits, n = [], 0
    for e in kalshi_events():
        n += 1
        ms = e.get("markets") or []
        hits += mono(e["event_ticker"], ms)
        if e.get("mutually_exclusive"):
            hits += allsides("K", e["event_ticker"], ms, taker_fee)
    return hits, n


def poly_events():
    s = requests.Session()
    for off in range(0, 20000, 500):
        try:
            r = s.get(f"{GAMMA}/events", params={"closed": "false", "active": "true", "limit": 500, "offset": off}, timeout=40)
        except requests.RequestException:
            return
        if r.status_code != 200:
            return
        js = r.json()
        if not js:
            return
        for e in js:
            yield e
        time.sleep(0.3)


def poly_book_top(token: str) -> tuple[float, float, float, float]:
    """(best bid, bid size, best ask, ask size) for one outcome token from the CLOB."""
    try:
        r = requests.get(f"{CLOB}/book", params={"token_id": token}, timeout=20)
        b = r.json() if r.status_code == 200 else {}
    except (requests.RequestException, ValueError):
        b = {}
    bids = sorted(((f(x["price"]), f(x["size"])) for x in b.get("bids", [])), reverse=True)
    asks = sorted((f(x["price"]), f(x["size"])) for x in b.get("asks", []))
    bb, bs = bids[0] if bids else (0.0, 0.0)
    aa, as_ = asks[0] if asks else (1.0, 0.0)
    return bb, bs, aa, as_


def scan_poly() -> tuple[list[dict], int]:
    hits, n = [], 0
    for e in poly_events():
        if not e.get("negRisk"):
            continue
        ms = [m for m in e.get("markets", []) if m.get("active") and not m.get("closed") and m.get("enableOrderBook")]
        if len(ms) < 2:
            continue
        n += 1
        bid = sum(f(m.get("bestBid"), 0.0) for m in ms)
        ask = sum(f(m.get("bestAsk"), 1.0) for m in ms)
        if bid <= 1.0 and ask >= 1.0:
            continue  # cheap pre-filter from the listing; confirm with real books below
        legs = []
        for m in ms:
            try:
                tok = json.loads(m.get("clobTokenIds") or "[]")[0]
            except (ValueError, IndexError):
                tok = None
            if not tok:
                legs = []; break
            bb, bs, aa, as_ = poly_book_top(tok)
            legs.append({"ticker": m.get("slug"), "yes_bid_dollars": bb, "yes_bid_size_fp": bs, "yes_ask_dollars": aa,
                         "yes_ask_size_fp": as_, "close_time": m.get("endDate"), "status": "active"})
        if legs:
            hits += allsides("P", e.get("slug"), legs, lambda n_, p_: 0.0)
    return hits, n


def enrich(h: dict, now: pd.Timestamp) -> dict:
    close = pd.to_datetime(h.get("close"), utc=True, errors="coerce")
    days = max((close - now).total_seconds() / 86400, 1 / 24) if pd.notna(close) else float("nan")
    h["days_to_close"] = days
    h["ann_return"] = (h["profit"] / h["cost"]) * 365 / days if h["cost"] > 0 and days == days else float("nan")
    h["seen_utc"] = now.isoformat()
    return h


def summary(log: pd.DataFrame, now: pd.Timestamp) -> str:
    lines = [f"# Round 43: riskless arbitrage scanner (Kalshi + Polymarket)", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: [PROTOCOL_ROUND43.md](../PROTOCOL_ROUND43.md).", ""]
    if log.empty:
        return "\n".join(lines + ["No opportunities logged yet."]) + "\n"
    g = log[log.profit >= MIN_PROFIT].copy()
    g["key"] = g.kind + "|" + g.legs.str.replace(r"@[0-9.]+", "", regex=True)
    by = g.groupby("key").agg(kind=("kind", "first"), event=("event", "first"), first=("seen_utc", "min"),
                              last=("seen_utc", "max"), passes=("seen_utc", "count"), best_profit=("profit", "max"),
                              size=("n", "max"), days=("days_to_close", "min"), ann=("ann_return", "max"))
    riskless = by[~by.kind.str.endswith("YESALL")]
    lines += [f"Distinct riskless opportunities ≥ ${MIN_PROFIT:.2f}: **{len(riskless)}**, best-case total if each taken once: "
              f"**${riskless.best_profit.sum():,.2f}**. Conditional (YES-all, needs exhaustive outcomes): {len(by) - len(riskless)}.", ""]
    for k in ("K-MONO", "K-NOALL", "P-NOALL", "K-YESALL", "P-YESALL"):
        x = by[by.kind == k].sort_values("best_profit", ascending=False).head(15)
        if len(x):
            lines += [f"## {k}", "", x.drop(columns=["kind"]).round(3).to_markdown(index=False), ""]
    return "\n".join(lines) + "\n"


def commit(now):
    for c in (["git", "add", LOG, REPORT], ["git", "commit", "-q", "-m", f"round43: arb log {now:%Y-%m-%dT%H:%MZ} [skip ci]"],
              ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]):
        try:
            if subprocess.run(c, cwd=ROOT, timeout=120).returncode != 0 and c[1] == "commit":
                return
        except subprocess.TimeoutExpired:
            return


def run():
    t0, last = time.time(), time.time()
    log = pd.read_csv(LOG) if os.path.exists(LOG) else pd.DataFrame()
    while time.time() - t0 < RUN_SECONDS:
        now = pd.Timestamp.now(tz="UTC")
        new = []
        for name, fn in (("kalshi", scan_kalshi), ("polymarket", scan_poly)):
            try:
                hits, n = fn()
                new += [enrich(h, now) for h in hits]
                print(f"{now:%H:%M:%S} {name}: {n} events, {len(hits)} hits, "
                      f"best ${max([h['profit'] for h in hits], default=0):.2f}", flush=True)
            except Exception as e:
                print(f"{now:%H:%M:%S} {name} failed: {e!r}", flush=True)
        if new:
            log = pd.concat([log, pd.DataFrame(new)], ignore_index=True)
            log.to_csv(LOG, index=False)
        if os.environ.get("R43_COMMIT") == "1" and time.time() - last > 1800:
            open(REPORT, "w").write(summary(log, now)); commit(now); last = time.time()
        time.sleep(max(0.0, PASS_SECONDS - (time.time() - now.timestamp())))
    now = pd.Timestamp.now(tz="UTC")
    open(REPORT, "w").write(summary(log, now))
    if os.environ.get("R43_COMMIT") == "1":
        commit(now)


if __name__ == "__main__":
    run()
