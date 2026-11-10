"""Round 46 (PROTOCOL_ROUND46.md): paper maker bids on the 85-95c favourite in Sports and Entertainment markets."""
from __future__ import annotations
import json, math, os, re, subprocess, time
import numpy as np
import pandas as pd

from edge import weather as wx
from edge import lip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "paper", "r46_state.json")
DONE = os.path.join(ROOT, "paper", "r46_settled.csv")
REPORT = os.path.join(ROOT, "paper", "ROUND46_FAV.md")
CATS = {"Sports", "Entertainment"}
LO, HI, STAKE, MAX_OPEN, BUDGET = 0.85, 0.95, 200.0, 50, 10_000.0
SCAN_EVERY, STEP = 900, 120
PER_EVENT = 3            # strikes/props of one game move together (Nov 8 lesson)
RUN_SECONDS = int(os.environ.get("R46_SECONDS", str(5 * 3600 + 40 * 60)))


def get(path, params=None):
    r = wx._get(f"{wx.KALSHI}/{path}", params)
    return r.json() if r is not None and r.status_code == 200 else None


def series_in_cats() -> list[str]:
    j = get("series") or {}
    return [s["ticker"] for s in j.get("series", []) if s.get("category") in CATS]


def open_markets(series: str, now: pd.Timestamp) -> list[dict]:
    out, cursor = [], None
    for _ in range(10):
        p = {"series_ticker": series, "status": "open", "limit": 1000, "max_close_ts": int((now + pd.Timedelta(days=7)).timestamp())}
        if cursor:
            p["cursor"] = cursor
        j = get("markets", p)
        if not j:
            break
        out += j.get("markets", [])
        cursor = j.get("cursor")
        if not cursor or not j.get("markets"):
            break
    return out


def favourite(m: dict):
    """(side, best bid, size at that bid) if the favourite's best bid is inside [LO, HI], else None."""
    yb, ya = lip.fnum(m.get("yes_bid_dollars")), lip.fnum(m.get("yes_ask_dollars"), 1.0)
    if LO - 1e-9 <= yb <= HI + 1e-9:
        return "yes", yb, lip.fnum(m.get("yes_bid_size_fp"))
    nb = round(1 - ya, 4) if ya < 1 else 0.0
    if LO - 1e-9 <= nb <= HI + 1e-9:
        return "no", nb, lip.fnum(m.get("yes_ask_size_fp"))
    return None


def new_order(m: dict, side: str, px: float, ahead: float, cat: str, now: pd.Timestamp) -> dict:
    q = math.floor(STAKE / px)
    o = {"ticker": m["ticker"], "event": m.get("event_ticker") or m["ticker"].rsplit("-", 1)[0], "category": cat, "side": side,
         "close": m.get("close_time"), "placed": now.isoformat(), "q": q, "yes_px": None, "no_px": None, "yes_ahead": 0.0, "no_ahead": 0.0,
         "inv_yes": 0.0, "inv_no": 0.0, "cost_yes": 0.0, "cost_no": 0.0, "realized": 0.0, "fees": 0.0, "resting": True}
    o[f"{side}_px"], o[f"{side}_ahead"] = px, ahead
    return o


def committed(o):
    rest = (o["q"] - o[f"inv_{o['side']}"]) * o[f"{o['side']}_px"] if o["resting"] and o.get(f"{o['side']}_px") else 0.0
    return rest + o["cost_yes"] + o["cost_no"]


def ladder(ticker: str) -> str:
    return re.sub(r"[0-9.]+$", "", ticker)


def scan(st, now, cat_of):
    held = {o["ticker"] for o in st["orders"]}
    ladders = {ladder(o["ticker"]) for o in st["orders"]}
    per_event: dict = {}
    for o in st["orders"]:
        per_event[o["event"]] = per_event.get(o["event"], 0) + 1
    used = sum(committed(o) for o in st["orders"])
    n_open = sum(1 for o in st["orders"] if o["resting"])
    order = list(cat_of.items())
    np.random.default_rng(int(now.timestamp()) // SCAN_EVERY).shuffle(order)
    for s, cat in order:
        for m in open_markets(s, now):
            if n_open >= MAX_OPEN or used + STAKE > BUDGET:
                return
            if m["ticker"] in held or pd.Timestamp(m["close_time"]) <= now + pd.Timedelta(minutes=10):
                continue
            ev = m.get("event_ticker") or m["ticker"].rsplit("-", 1)[0]
            if ladder(m["ticker"]) in ladders or per_event.get(ev, 0) >= PER_EVENT:
                continue
            fv = favourite(m)
            if not fv:
                continue
            side, px, ahead = fv
            st["orders"].append(new_order(m, side, px, ahead, cat, now))
            held.add(m["ticker"]); ladders.add(ladder(m["ticker"])); per_event[ev] = per_event.get(ev, 0) + 1
            used += STAKE; n_open += 1


def step(st, now):
    keep = []
    for o in st["orders"]:
        side = o["side"]
        info = get(f"markets/{o['ticker']}") or {}
        m = info.get("market", {})
        if m.get("result") in ("yes", "no"):
            filled = o[f"inv_{side}"]
            if filled > 0:
                pnl = filled * (1.0 if m["result"] == side else 0.0) - o[f"cost_{side}"] - o["fees"]
                rec = {k: o[k] for k in ("ticker", "event", "category", "side", "placed", "close")}
                rec.update(filled=filled, avg_px=o[f"cost_{side}"] / filled, result=m["result"], pnl=round(pnl, 2), settled=now.isoformat())
                pd.DataFrame([rec]).to_csv(DONE, mode="a", header=not os.path.exists(DONE), index=False)
            continue
        if o["resting"]:
            tr = (get("markets/trades", {"ticker": o["ticker"], "limit": 1000, "min_ts": int(st["last"])}) or {}).get("trades", [])
            lip.apply_trades(o, tr)
            closed = pd.Timestamp(o["close"]) <= now or m.get("status") not in (None, "active")
            if o[f"inv_{side}"] >= o["q"] or closed:
                o["resting"] = False
            else:   # re-peg to the current best bid of our side while it stays in the band
                fv = favourite(m) if m else None
                if fv and fv[0] == side:
                    if abs(fv[1] - o[f"{side}_px"]) > 1e-9:
                        o[f"{side}_px"], o[f"{side}_ahead"], o[f"filled_{side}_at_peg"] = fv[1], fv[2], 0.0
                else:
                    o["resting"] = False
        if o["resting"] or o[f"inv_{side}"] > 0:
            keep.append(o)
    st["orders"] = keep


def summary(st, now) -> str:
    lines = ["# Round 46: paper maker bids on the 85–95c favourite (Sports, Entertainment)", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: [PROTOCOL_ROUND46.md](../PROTOCOL_ROUND46.md). $10,000 budget, ~$200 a market.", ""]
    resting = sum(1 for o in st["orders"] if o["resting"])
    held = [o for o in st["orders"] if o[f"inv_{o['side']}"] > 0]
    lines.append(f"Now: {resting} resting bids, {len(held)} filled positions awaiting settlement "
                 f"(${sum(o['cost_yes'] + o['cost_no'] for o in held):,.0f} at cost).")
    if os.path.exists(DONE):
        d = pd.read_csv(DONE)
        e = d.groupby("event").agg(pnl=("pnl", "sum"), risk=("filled", "sum"))
        risk = (d.filled * d.avg_px).groupby(d.event).sum()
        ret = e.pnl.sum() / risk.sum() if risk.sum() else float("nan")
        resid = e.pnl - ret * risk
        t = ret / (np.sqrt((resid ** 2).sum()) / risk.sum()) if len(e) > 1 else float("nan")
        lines += ["", f"Settled: **{len(d)} markets, {d.event.nunique()} events, P&L ${d.pnl.sum():,.2f}**, "
                      f"return {ret:.2%} per dollar (event-clustered t {t:.1f}), win rate {(d.pnl > 0).mean():.0%}.", "",
                  d.assign(day=pd.to_datetime(d.settled).dt.date).groupby(["day", "category"]).pnl.agg(["count", "sum"]).round(2).to_markdown()]
    return "\n".join(lines) + "\n"


def commit(now):
    paths = [p for p in (STATE, DONE, REPORT) if os.path.exists(p)]
    for c in (["git", "add", *paths], ["git", "commit", "-q", "-m", f"round46: fav ledger {now:%Y-%m-%dT%H:%MZ} [skip ci]"],
              ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]):
        try:
            if subprocess.run(c, cwd=ROOT, timeout=120).returncode != 0 and c[1] == "commit":
                return
        except subprocess.TimeoutExpired:
            return


def run():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"orders": [], "last": time.time() - STEP, "scanned": 0}
    cat_of = {}
    j = get("series") or {}
    for s in j.get("series", []):
        if s.get("category") in CATS:
            cat_of[s["ticker"]] = s["category"]
    print(f"{len(cat_of)} series in {sorted(CATS)}", flush=True)
    t0, last_commit = time.time(), time.time()
    while time.time() - t0 < RUN_SECONDS:
        now = pd.Timestamp.now(tz="UTC")
        try:
            step(st, now)
            st["last"] = now.timestamp()
            if time.time() - st["scanned"] > SCAN_EVERY:
                scan(st, now, cat_of); st["scanned"] = time.time()
                print(f"{now:%H:%M} orders {len(st['orders'])}, resting {sum(o['resting'] for o in st['orders'])}", flush=True)
            json.dump(st, open(STATE, "w"))
        except Exception as e:
            print(f"{now:%H:%M:%S} step failed: {e!r}", flush=True)
        if os.environ.get("R46_COMMIT") == "1" and time.time() - last_commit > 1800:
            open(REPORT, "w").write(summary(st, now)); commit(now); last_commit = time.time()
        time.sleep(max(0.0, STEP - (time.time() - now.timestamp())))
    now = pd.Timestamp.now(tz="UTC")
    open(REPORT, "w").write(summary(st, now))
    if os.environ.get("R46_COMMIT") == "1":
        commit(now)


if __name__ == "__main__":
    run()
