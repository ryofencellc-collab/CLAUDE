"""Live trader for the Round 21/22 edge on Kalshi 15-minute crypto markets.

1:1 with the paper bot: the signal (markets, spot, z, threshold, side, cancel rule) is imported from
edge.paper21 and not re-implemented. What this adds is the account side: authenticated orders, sizing from
the real balance, and hard risk rules.

Modes:
  DRY (default): every decision is made and logged with the order it would send; nothing is sent.
                 With API keys present it also reads the real balance and positions (read-only).
  LIVE:          only when env LIVE21=1 AND both secrets are set. Orders are post-only limit buys at 99c.

Risk rules (persisted in paper/live21_state.json):
  - one resting order or open position at a time, so the worst case is one market's stake;
  - size = min(MAX_CONTRACTS, 95% of balance / 0.99), halved for 7 days after a losing market;
  - any losing filled market: no new orders for 24 hours;
  - realised loss today beyond DAILY_STOP of the starting balance: no new orders until tomorrow (UTC);
  - stale spot data, or a STOP file at paper/LIVE21_STOP: cancel everything and place nothing.
"""
import base64
import json
import math
import os
import time
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from edge import paper21 as sig

ROOT = Path(__file__).resolve().parent.parent / "paper"
LOG = ROOT / "live21_log.csv"
STATE = ROOT / "live21_state.json"
STOP = ROOT / "LIVE21_STOP"
SERIES = [s for s in sig.SERIES if s.endswith("15M")]  # capital-efficient part only (see PROTOCOL_ROUND22.md)
MAX_CONTRACTS = int(os.environ.get("LIVE21_MAX", 1000))
PRICE_CENTS = 99
DAILY_STOP = 0.10
PAUSE_HOURS, HALF_DAYS = 24, 7
API = "https://api.elections.kalshi.com"
BASE = "/trade-api/v2"
LOG_COLS = ["time_utc", "mode", "event", "ticker", "side", "count", "z", "spot", "balance", "detail"]


# ---------------------------------------------------------------------- Kalshi client
class Kalshi:
    """Minimal authenticated client (RSA-PSS signed headers, as Kalshi's API requires)."""

    def __init__(self, key_id: str | None, private_key_pem: str | None):
        self.key_id = key_id
        self.key = None
        if key_id and private_key_pem:
            from cryptography.hazmat.primitives import serialization
            self.key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
        self.s = requests.Session()

    @property
    def authed(self) -> bool:
        return self.key is not None

    def _headers(self, method: str, path: str) -> dict:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        ts = str(int(time.time() * 1000))
        msg = (ts + method + path.split("?")[0]).encode()
        sig_bytes = self.key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                   salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
        return {"KALSHI-ACCESS-KEY": self.key_id, "KALSHI-ACCESS-TIMESTAMP": ts,
                "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig_bytes).decode(), "Content-Type": "application/json"}

    def call(self, method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict:
        full = BASE + path
        r = self.s.request(method, API + full, headers=self._headers(method, full), params=params,
                           data=json.dumps(body) if body is not None else None, timeout=20)
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        return r.json() if r.text else {}

    def balance_usd(self) -> float:
        return float(self.call("GET", "/portfolio/balance").get("balance", 0)) / 100

    def resting(self) -> list[dict]:
        return self.call("GET", "/portfolio/orders", params={"status": "resting", "limit": 200}).get("orders", [])

    def positions(self) -> list[dict]:
        ps = self.call("GET", "/portfolio/positions", params={"limit": 200}).get("market_positions", [])
        return [p for p in ps if float(p.get("position_fp") or p.get("position") or 0) != 0]

    def buy(self, ticker: str, side: str, count: int, cents: int = PRICE_CENTS) -> dict:
        body = order_body(ticker, side, count, cents)
        return self.call("POST", "/portfolio/orders", body=body).get("order", {})

    def cancel(self, order_id: str) -> None:
        self.call("DELETE", f"/portfolio/orders/{order_id}")


def order_body(ticker: str, side: str, count: int, cents: int = PRICE_CENTS) -> dict:
    """Post-only limit buy for the decided side: it rests in the book and can never take liquidity."""
    body = {"ticker": ticker, "action": "buy", "side": side, "count": int(count), "type": "limit",
            "client_order_id": f"r21-{uuid.uuid4().hex[:16]}", "post_only": True}
    body["yes_price" if side == "yes" else "no_price"] = int(cents)
    return body


# ---------------------------------------------------------------------- risk state
def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"pause_until": 0.0, "half_until": 0.0, "day": "", "day_start_balance": 0.0, "day_loss": 0.0,
            "open": None, "results": []}


def save_state(st: dict) -> None:
    STATE.write_text(json.dumps(st, indent=1))


def size_for(balance: float, st: dict, now: float) -> int:
    n = min(MAX_CONTRACTS, math.floor(balance * 0.95 / (PRICE_CENTS / 100)))
    if now < st["half_until"]:
        n //= 2
    return max(0, n)


def blocked(st: dict, now: float, balance: float) -> str | None:
    if STOP.exists():
        return "stop file present"
    if now < st["pause_until"]:
        return "paused after a losing market"
    if st["day_start_balance"] > 0 and st["day_loss"] >= DAILY_STOP * st["day_start_balance"]:
        return "daily loss limit"
    return None


def record_result(st: dict, now: float, pnl: float) -> None:
    """Apply the pause/half-size/daily-stop rules to a settled market's P&L."""
    st["results"].append({"t": now, "pnl": pnl})
    if pnl < 0:
        st["day_loss"] += -pnl
        st["pause_until"] = now + PAUSE_HOURS * 3600
        st["half_until"] = st["pause_until"] + HALF_DAYS * 86400


# ---------------------------------------------------------------------- loop
def log(mode: str, event: str, ticker="", side="", count=0, z=np.nan, spot=np.nan, balance=np.nan, detail=""):
    row = dict(time_utc=pd.Timestamp.now(tz="UTC").isoformat(), mode=mode, event=event, ticker=ticker, side=side,
               count=count, z=z, spot=spot, balance=balance, detail=str(detail)[:300])
    pd.DataFrame([row])[LOG_COLS].to_csv(LOG, mode="a", header=not (LOG.exists() and LOG.stat().st_size), index=False)
    print(f"{row['time_utc'][:19]} {mode} {event} {ticker} {side} {count} {detail}", flush=True)


def decide(now: pd.Timestamp):
    """The paper bot's placement rule, unchanged: first 15-minute market whose side is decided at z >= Z."""
    spots = {sig.SERIES[s]: sig.spot_and_vol(sig.SERIES[s], now) for s in SERIES}
    for series in SERIES:
        s, v = spots[sig.SERIES[series]]
        if not np.isfinite(s):
            continue
        for m in sig.open_markets(series, now):
            zy, zn = sig.z_sides(m.get("strike_type"), m.get("floor_strike"), m.get("cap_strike"), s, v, m["_close"], now)
            if np.isfinite(zy) and zy >= sig.zmin(series):
                return m, series, "yes", zy, s
            if np.isfinite(zn) and zn >= sig.zmin(series):
                return m, series, "no", zn, s
    return None


def still_decided(o: dict, now: pd.Timestamp) -> bool:
    s, v = sig.spot_and_vol(sig.SERIES[o["series"]], now)
    if not np.isfinite(s):
        return False  # stale data: treat as not decided, so the order is pulled
    zy, zn = sig.z_sides(o["strike_type"], o["floor"], o["cap"], s, v, pd.Timestamp(o["close"]), now)
    z = zy if o["side"] == "yes" else zn
    return bool(np.isfinite(z) and z >= sig.zmin(o["series"]))


def settle(api: Kalshi, st: dict, mode: str, now: pd.Timestamp) -> None:
    """After the open market closes, read its result and our fill, and apply the risk rules."""
    o = st["open"]
    if not o or now < pd.Timestamp(o["close"]) + pd.Timedelta(minutes=2):
        return
    r = sig.wx._get(f"{sig.wx.KALSHI}/markets/{o['ticker']}")
    m = r.json().get("market", {}) if r is not None and r.status_code == 200 else {}
    if m.get("result") not in ("yes", "no"):
        return
    if mode == "LIVE" and api.authed:
        fills = api.call("GET", "/portfolio/fills", params={"ticker": o["ticker"], "limit": 200}).get("fills", [])
        filled = sum(float(f.get("count_fp") or f.get("count") or 0) for f in fills if f.get("action") == "buy")
    else:  # dry run: the paper bot's fill accounting, so dry P&L is comparable 1:1 with the paper ledger
        until = pd.Timestamp(o["cancelled_at"]) if o.get("cancelled_at") else pd.Timestamp(o["close"])
        seen = sig.seen_since(o["ticker"], o["side"], pd.Timestamp(o["placed"]), until)
        q = o.get("queue_ahead")
        filled = float(min(o["count"], max(0.0, seen - (float(q) if q is not None and np.isfinite(q) else 0.0))))
    right = m["result"] == o["side"]
    pnl = filled * ((1.0 if right else 0.0) - PRICE_CENTS / 100) - (sig.r15._maker_fee(filled, 0.99) if filled else 0.0)
    record_result(st, now.timestamp(), pnl)
    log(mode, "settled", o["ticker"], o["side"], filled, detail=f"result={m['result']} pnl={pnl:.2f}")
    st["open"] = None


def step(api: Kalshi, st: dict, mode: str, now: pd.Timestamp) -> None:
    day = now.date().isoformat()
    balance = api.balance_usd() if api.authed else MAX_CONTRACTS * 1.05
    if st["day"] != day:
        st.update(day=day, day_start_balance=balance, day_loss=0.0)
    settle(api, st, mode, now)
    o = st["open"]
    if o and now < pd.Timestamp(o["close"]):
        if o.get("cancelled"):
            return
        if not still_decided(o, now) or STOP.exists():
            if mode == "LIVE" and o.get("order_id"):
                api.cancel(o["order_id"])
            log(mode, "cancel", o["ticker"], o["side"], o["count"], detail="z below threshold, stale data or stop")
            o["cancelled"] = True
            o["cancelled_at"] = now.isoformat()
        return
    if o:
        return  # closed, waiting for its result
    why = blocked(st, now.timestamp(), balance)
    if why:
        return
    pick = decide(now)
    if not pick:
        return
    m, series, side, z, spot = pick
    count = size_for(balance, st, now.timestamp())
    if count < 1:
        log(mode, "skip", m["ticker"], side, 0, z, spot, balance, "balance too small")
        return
    order_id = None
    if mode == "LIVE":
        order = api.buy(m["ticker"], side, count)
        order_id = order.get("order_id")
    log(mode, "place", m["ticker"], side, count, round(z, 2), spot, balance, json.dumps(order_body(m["ticker"], side, count)))
    st["open"] = dict(ticker=m["ticker"], series=series, side=side, count=count, close=m["_close"].isoformat(),
                      strike_type=m.get("strike_type"), floor=m.get("floor_strike"), cap=m.get("cap_strike"),
                      order_id=order_id, placed=now.isoformat(), queue_ahead=sig.queue_ahead(m["ticker"], side))


def summary() -> str:
    """paper/LIVE21.md: what the trader did, from its own log."""
    if not (LOG.exists() and LOG.stat().st_size):
        return "# Live trader (Round 21/22)\n\nNo activity yet.\n"
    g = pd.read_csv(LOG)
    st = g[g["event"] == "settled"].copy()
    st["pnl"] = st["detail"].str.extract(r"pnl=(-?[0-9.]+)")[0].astype(float)
    filled = st[st["count"] > 0]
    mode = g["mode"].iloc[-1]
    lines = ["# Live trader (Round 21/22): 15-minute crypto markets", "",
             f"Mode now: **{mode}** (DRY = decides and logs, sends nothing). Log: [live21_log.csv](live21_log.csv).", "",
             "| | |", "|---|---|",
             f"| Orders placed | {int((g['event'] == 'place').sum())} |",
             f"| Cancelled before close | {int((g['event'] == 'cancel').sum())} |",
             f"| Settled markets / with fills | {len(st)} / {len(filled)} |",
             f"| Losing filled markets | {int((filled['pnl'] < 0).sum())} |",
             f"| **P&L** | **${st['pnl'].sum():+,.2f}** |",
             f"| Errors | {int((g['event'] == 'error').sum())} |", ""]
    if len(st):
        st["day"] = st["time_utc"].str[:10]
        lines += ["| Day | Settled | Filled | P&L |", "|---|---:|---:|---:|"]
        lines += [f"| {d} | {len(x)} | {int((x['count'] > 0).sum())} | ${x['pnl'].sum():+.2f} |" for d, x in st.groupby("day")]
    return "\n".join(lines) + "\n"


def run():
    key_id, pem = os.environ.get("KALSHI_KEY_ID"), os.environ.get("KALSHI_PRIVATE_KEY")
    api = Kalshi(key_id, pem)
    mode = "LIVE" if os.environ.get("LIVE21") == "1" and api.authed else "DRY"
    st = load_state()
    log(mode, "start", detail=f"authed={api.authed} max={MAX_CONTRACTS} series={','.join(SERIES)}")
    if mode == "LIVE":
        for o in api.resting():  # clean slate: nothing of ours rests from a previous job
            if str(o.get("client_order_id", "")).startswith("r21-"):
                api.cancel(o["order_id"])
                log(mode, "cancel", o.get("ticker", ""), detail="startup clean-up")
    t0 = time.time()
    seconds = int(os.environ.get("LIVE21_SECONDS", 20700))
    while time.time() - t0 < seconds:
        now = pd.Timestamp.now(tz="UTC")
        try:
            step(api, st, mode, now)
        except Exception as e:  # never die silently with an order resting: log, pull orders, carry on
            log(mode, "error", detail=repr(e))
            if mode == "LIVE" and st.get("open") and st["open"].get("order_id"):
                try:
                    api.cancel(st["open"]["order_id"])
                except Exception:
                    pass
        save_state(st)
        if int(time.time() - t0) % 600 < 5:
            (ROOT / "LIVE21.md").write_text(summary())
        time.sleep(max(0.0, 5 - (time.time() - now.timestamp())))
    log(mode, "stop", detail="job time limit")
    (ROOT / "LIVE21.md").write_text(summary())


def selftest() -> None:
    """Checks keys, signing and the order format with almost no risk: reads the balance, rests a 1-contract
    buy at 1c on an open 15-minute market, confirms it rests, then cancels it."""
    api = Kalshi(os.environ.get("KALSHI_KEY_ID"), os.environ.get("KALSHI_PRIVATE_KEY"))
    if not api.authed:
        raise SystemExit("selftest needs the KALSHI_KEY_ID and KALSHI_PRIVATE_KEY secrets")
    print(f"balance ${api.balance_usd():,.2f}")
    now = pd.Timestamp.now(tz="UTC")
    m = next((m for s in SERIES for m in sig.open_markets(s, now)), None)
    if m is None:
        raise SystemExit("no open 15-minute market right now; try again in a minute")
    order = api.buy(m["ticker"], "yes", 1, cents=1)
    print(f"placed test order {order.get('order_id')} on {m['ticker']}: status {order.get('status')}")
    ids = [o.get("order_id") for o in api.resting()]
    print("resting:", order.get("order_id") in ids)
    api.cancel(order["order_id"])
    print("cancelled; selftest OK")


if __name__ == "__main__":
    import sys
    selftest() if sys.argv[1:] == ["selftest"] else run()
