"""Live trader for the Round 21/22/25 edge on Kalshi 15-minute crypto markets.

Signal: markets, spot price and z come from edge.paper21 (the paper bot's code, imported, not copied).
Entry, cancel and size follow Round 25: the |z| x minutes-left reversal table (control/r25_zbins.json),
entry only when the reversal risk is < 0.3%, cancel when it reaches 0.3%, size = min(Claude's stake cap,
Kelly(risk)). Without the table it falls back to Round 21's z >= 6.

Control: Claude's control/live21.json (live / stop / stake_fraction / max_contracts), re-read from GitHub
every minute. LIVE only with both Kalshi secrets, "live": true and no owner veto (repo variable LIVE21=0).
Otherwise DRY: every decision is made and logged, nothing is sent.

Risk rules: post-only 99c limit buys that expire at the market's close; one market at a time; never the
same market twice; 24 h pause then 7 days at half size after any losing market; no new orders after losing
10% of the day's starting balance; stale prices or a stop: pull the order and place nothing. In LIVE the
loss rules are rebuilt from Kalshi's own settlement records every minute. Full list: AUDIT_LIVE21.md.
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
from edge import prices as px

ROOT = Path(__file__).resolve().parent.parent / "paper"
LOG = ROOT / "live21_log.csv"
STATE = ROOT / "live21_state.json"
STOP = ROOT / "LIVE21_STOP"
CONTROL = ROOT.parent / "control" / "live21.json"  # Claude's switch; re-read from GitHub every minute
ZBINS = ROOT.parent / "control" / "r25_zbins.json"  # Round 25 reversal table (|z| x minutes left)
P_MAX = 0.003  # Round 25's chosen entry gate: enter only when the table's reversal risk is below 0.3%
SERIES = [s for s in sig.SERIES if s.endswith("15M")]  # capital-efficient part only (see PROTOCOL_ROUND22.md)
MAX_CONTRACTS = int(os.environ.get("LIVE21_MAX", 1000))
PRICE_CENTS = 99
ORDERS_V2 = "/portfolio/events/orders"  # Kalshi API 3.36: create (POST) and cancel (DELETE /{id}); legacy POST is gone
DAILY_STOP = 0.10
PAUSE_HOURS, HALF_DAYS = 24, 7
# control/RULES.md, enforced by the bot itself from Kalshi's settlement records (no one has to be watching)
FLOOR = 0.70             # equity ever <= 70% of the deposit: stop for good
LOSSES_TO_STOP, LOSS_WINDOW_DAYS = 2, 7
STAKE_START, STAKE_GROWN, STAKE_AFTER_LOSS = 0.5, 0.95, 0.25
GROW_DAYS, AFTER_LOSS_DAYS = 14, 14
API = "https://api.elections.kalshi.com"
BASE = "/trade-api/v2"
LOG_COLS = ["time_utc", "mode", "event", "ticker", "side", "count", "z", "spot", "balance", "detail"]


_table = {}


def flip_risk(az: float, tau: float) -> float:
    """Round 25: historical reversal rate for this |z| and minutes left (bins are right-closed, as fitted).
    Without the table, fall back to Round 21's rule: z >= Z counts as decided (risk 0), below it as not (1)."""
    if not _table:
        if ZBINS.exists():
            t = json.loads(ZBINS.read_text())
            # a bigger lead is never riskier: within each minutes-left column, risk can only fall as |z| rises.
            # (Sparse high-|z| cells otherwise show a prior near 50% and would cancel our safest orders.)
            t["rate"] = np.minimum.accumulate(np.asarray(t["rate"], dtype=float), axis=0).tolist()
            _table.update(t)
        else:
            return 0.0 if az >= sig.Z else 1.0
    if not (np.isfinite(az) and np.isfinite(tau)):
        return 1.0
    zi = int(np.searchsorted(_table["z_edges"], az, side="left")) - 1
    ti = int(np.searchsorted(_table["tau_edges"], tau, side="left")) - 1
    if zi < 0 or ti < 0 or zi >= len(_table["rate"]) or ti >= len(_table["rate"][0]):
        return 1.0
    return float(_table["rate"][zi][ti])


def kelly(p: float) -> float:
    """Full Kelly for a 99c bet that pays 1c or loses 99c (Round 25's chosen multiplier is 1.0)."""
    return max(0.0, (1 - p) - p * (0.99 / 0.01))


def num(d: dict, *keys, scale: float = 1.0) -> float:
    """First present numeric field among keys (Kalshi returns some fields as fixed-point strings)."""
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            try:
                return float(v) * scale
            except (TypeError, ValueError):
                continue
    return 0.0


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
        """Available cash, all exchange shards (Kalshi API 3.36: balance_dollars string, or balance in cents)."""
        b = self.call("GET", "/portfolio/balance")
        return num(b, "balance_dollars") if b.get("balance_dollars") is not None else num(b, "balance", scale=0.01)

    def resting(self) -> list[dict]:
        return self.pages("/portfolio/orders", "orders", {"status": "resting", "limit": 200})

    def positions(self) -> list[dict]:
        ps = self.pages("/portfolio/positions", "market_positions", {"limit": 200, "count_filter": "position"})
        return [p for p in ps if num(p, "position_fp", "position") != 0]

    def pages(self, path: str, key: str, params: dict, max_pages: int = 50) -> list[dict]:
        """Every page of a cursor-paginated list endpoint."""
        out, cursor = [], None
        for _ in range(max_pages):
            p = {**params, **({"cursor": cursor} if cursor else {})}
            j = self.call("GET", path, params=p)
            out += j.get(key, [])
            cursor = j.get("cursor")
            if not cursor or not j.get(key):
                break
        return out

    def filled(self, ticker: str, order_id: str | None = None) -> float:
        """Contracts our order bought. By order id when known (V2: buying NO is an 'ask' on the YES book, so the
        legacy action/side fields cannot be trusted to say 'buy'); otherwise every fill on the ticker."""
        params = {"order_id": order_id, "limit": 200} if order_id else {"ticker": ticker, "limit": 200}
        fills = self.pages("/portfolio/fills", "fills", params)
        return sum(num(f, "count_fp", "count") for f in fills
                   if (f.get("order_id") == order_id if order_id else f.get("ticker", ticker) == ticker))

    def recent_settlement_pnls(self, since: float) -> list[tuple[float, float]]:
        """(settled unix time, P&L in dollars) for our settlements since `since`."""
        out = []
        for x in self.pages("/portfolio/settlements", "settlements", {"limit": 200, "min_ts": int(since)}):
            t = pd.Timestamp(x.get("settled_time")).timestamp() if x.get("settled_time") else 0
            if t < since:
                continue
            revenue = num(x, "revenue", scale=0.01)
            cost = (num(x, "yes_total_cost_dollars") or num(x, "yes_total_cost", scale=0.01)) + \
                (num(x, "no_total_cost_dollars") or num(x, "no_total_cost", scale=0.01))
            fee = num(x, "fee_cost")  # 3.36: fee_cost is a fixed-point DOLLAR string
            out.append((t, revenue - cost - fee))
        return out

    def buy(self, ticker: str, side: str, count: int, cents: int = PRICE_CENTS, expires: float | None = None) -> dict:
        """Create Order V2 (POST /portfolio/events/orders). Returns {order_id, client_order_id, fill_count,
        remaining_count, status} with status 'resting' or 'executed'."""
        body = order_body(ticker, side, count, cents, expires)
        j = self.call("POST", ORDERS_V2, body=body)
        if not j.get("order_id"):
            raise RuntimeError(f"POST {ORDERS_V2} -> no order_id in response: {str(j)[:200]}")
        left = num(j, "remaining_count", "remaining_count_fp")
        return {**j, "status": "resting" if left > 0 else "executed"}

    def cancel(self, order_id: str, ticker: str | None = None) -> None:
        """Cancel Order V2. The market ticker lets Kalshi route it to the right exchange shard."""
        try:
            self.call("DELETE", f"{ORDERS_V2}/{order_id}", params={"market_ticker": ticker} if ticker else None)
        except RuntimeError as e:  # already filled, expired or cancelled: nothing left to pull
            if "-> 404" not in str(e) and "-> 409" not in str(e):
                raise


def order_body(ticker: str, side: str, count: int, cents: int = PRICE_CENTS, expires: float | None = None) -> dict:
    """Create Order V2 body (Kalshi API 3.36), a post-only buy of the decided side at `cents`: it rests in the
    book and can never take liquidity. V2 quotes everything on the YES book: buying YES at 99c is a 'bid' at
    0.9900; buying NO at 99c is an 'ask' (sell YES) at 0.0100. With `expires` (the market's close) Kalshi drops
    it by itself even if this bot has died; cancel_order_on_pause pulls it if the exchange halts trading."""
    if side not in ("yes", "no") or not 1 <= int(cents) <= 99 or int(count) < 1:
        raise ValueError(f"bad order: side={side!r} cents={cents!r} count={count!r}")
    yes_px = int(cents) if side == "yes" else 100 - int(cents)
    body = {"ticker": ticker, "client_order_id": f"r21-{uuid.uuid4().hex[:16]}",
            "side": "bid" if side == "yes" else "ask", "count": str(int(count)), "price": f"{yes_px / 100:.4f}",
            "time_in_force": "good_till_canceled", "self_trade_prevention_type": "taker_at_cross",
            "post_only": True, "cancel_order_on_pause": True}
    if expires:
        body["expiration_time"] = int(expires)
    return body


# ---------------------------------------------------------------------- risk state
def load_state() -> dict:
    """Saved state, or safe defaults if it is missing or unreadable (in LIVE the loss rules are then rebuilt
    from Kalshi's settlement records)."""
    if STATE.exists():
        try:
            st = json.loads(STATE.read_text())
            if isinstance(st, dict) and "pause_until" in st:
                return st
        except ValueError:
            pass
    return {"pause_until": 0.0, "half_until": 0.0, "day": "", "day_start_balance": 0.0, "day_loss": 0.0,
            "open": None, "results": []}


def save_state(st: dict) -> None:
    STATE.write_text(json.dumps(st, indent=1))


_control_misses = [0]
CONTROL_MAX_MISSES = 5  # ~5 minutes without reaching GitHub: stop, because a stop could not reach us either


def _git(args: list[str], timeout: float = 60, **kw):
    """git with a time limit: a hung network call must never freeze the trading loop. None = failed/timed out."""
    import subprocess
    try:
        r = subprocess.run(["git", *args], cwd=ROOT.parent, timeout=timeout, **kw)
        return r if r.returncode == 0 else None
    except (subprocess.TimeoutExpired, OSError):
        return None


def read_control() -> dict:
    """control/live21.json, preferring the latest version on GitHub so a commit reaches a running job. On
    GitHub Actions, if GitHub cannot be reached CONTROL_MAX_MISSES times in a row, the answer is "stopped"."""
    text, remote_failed = None, False
    if os.environ.get("GITHUB_ACTIONS") == "true":
        ref = os.environ.get("GITHUB_REF_NAME", "")
        if _git(["fetch", "-q", "origin", ref], timeout=30):
            r = _git(["show", f"origin/{ref}:control/live21.json"], timeout=10, capture_output=True, text=True)
            text = r.stdout if r else None
        remote_failed = text is None
        _control_misses[0] = _control_misses[0] + 1 if remote_failed else 0
    if text is None and CONTROL.exists():
        text = CONTROL.read_text()
    try:
        c = json.loads(text) if text else {}
        if not isinstance(c, dict):
            c = {}
    except ValueError:
        c = {}
    try:
        frac = min(0.95, max(0.0, float(c.get("stake_fraction", 0.25))))
        cap = max(0, int(c.get("max_contracts", MAX_CONTRACTS)))
    except (TypeError, ValueError):
        frac, cap = 0.25, MAX_CONTRACTS
    try:
        deposit = float(c.get("deposit", 1000))
        deposit = deposit if deposit > 0 else 1000.0
    except (TypeError, ValueError):
        deposit = 1000.0
    try:
        since = pd.Timestamp(c.get("live_since")).timestamp() if c.get("live_since") else 0.0
    except (TypeError, ValueError):
        since = 0.0
    stop = bool(c.get("stop", True)) or _control_misses[0] >= CONTROL_MAX_MISSES
    # anything missing or unreadable means: not live, stopped, smallest stake
    return {"live": bool(c.get("live", False)) and not stop, "stop": stop, "stake_fraction": frac, "max_contracts": cap,
            "deposit": deposit, "live_since": since}


def live_allowed(api: "Kalshi", control: dict) -> bool:
    """LIVE only with both secrets, Claude's control file saying live, and no owner veto (LIVE21=0)."""
    return api.authed and control["live"] and os.environ.get("LIVE21") != "0"


def size_for(balance: float, st: dict, now: float, fraction: float = 0.95, cap: int | None = None) -> int:
    n = min(cap if cap is not None else MAX_CONTRACTS, math.floor(balance * fraction / (PRICE_CENTS / 100)))
    if now < st["half_until"]:
        n //= 2
    return max(0, n)


def blocked(st: dict, now: float, balance: float) -> str | None:
    if STOP.exists() or st.get("control_stop"):
        return "stopped by control"
    if st.get("gov_halt"):
        return f"stopped by the rules: {st['gov_halt']}"
    if now < st["pause_until"]:
        return "paused after a losing market"
    if st["day_start_balance"] > 0 and st["day_loss"] >= DAILY_STOP * st["day_start_balance"]:
        return "daily loss limit"
    return None


def governor(pnls: list[tuple[float, float]], deposit: float, live_since: float, now: float) -> tuple[float, str | None]:
    """control/RULES.md as code. pnls = (settled time, P&L $) of every settlement since going live.
    Returns (stake fraction, halt reason or None). Both are worked out from the whole history every time, so a
    halt never wears off by itself and survives lost state; only a new live_since (a fresh start) clears it."""
    pnls = sorted(pnls)
    equity = deposit
    for _, pnl in pnls:
        equity += pnl
        if equity <= FLOOR * deposit:
            return 0.0, f"equity fell to ${equity:,.2f} (floor {FLOOR:.0%} of ${deposit:,.0f})"
    losses = [t for t, pnl in pnls if pnl < 0]
    for a, b in zip(losses, losses[LOSSES_TO_STOP - 1:]):
        if b - a <= LOSS_WINDOW_DAYS * 86400:
            return 0.0, f"{LOSSES_TO_STOP} losing markets within {LOSS_WINDOW_DAYS} days"
    if losses and now - losses[-1] < AFTER_LOSS_DAYS * 86400:
        return STAKE_AFTER_LOSS, None
    start = live_since or (pnls[0][0] if pnls else now)  # no live_since: days count from the first settlement
    if now - start >= GROW_DAYS * 86400 and sum(p for _, p in pnls) >= 0:
        return STAKE_GROWN, None
    return STAKE_START, None


def govern(api: "Kalshi", st: dict, control: dict, now: float) -> None:
    """Apply the governor: stake = min(Claude's cap, the rules' stake); a halt blocks all new trades. If Kalshi
    cannot be read, keep the last answer (smallest stake until there is one)."""
    try:
        if api.authed and control.get("live"):
            pnls = api.recent_settlement_pnls(control["live_since"])
        else:  # dry run: the same rules on the paper ledger, so dry sizes exactly as live would
            pnls = [(r["t"], r["pnl"]) for r in st.get("results", []) if r["t"] >= control["live_since"]]
        stake, halt = governor(pnls, control["deposit"], control["live_since"], now)
        if api.authed and control.get("live"):
            audit_balance(api, st, pnls, control["live_since"])
        st["gov_stake"], st["gov_halt"] = stake, halt or (st.get("audit") or {}).get("halt")
    except Exception as e:
        log("LIVE" if api.authed else "DRY", "error", detail=f"governor: {e!r}")
    st["stake_fraction"] = min(st["stake_fraction"], st.get("gov_stake", STAKE_AFTER_LOSS))


AUDIT_CHECKS = 10  # minutes a mismatch must last (settlement records and cash can lag each other briefly)


def audit_balance(api: "Kalshi", st: dict, pnls: list[tuple[float, float]], live_since: float) -> None:
    """"Anything unexplained" (control/RULES.md) as code: whenever we hold nothing, cash must have moved by
    exactly what Kalshi's settlement records say since the last such check (within max($1, 1%)). A mismatch
    that lasts AUDIT_CHECKS minutes (a deposit or withdrawal nobody recorded, a trade this bot did not make,
    or a bookkeeping error) halts trading until a fresh start (new live_since). Compared step by step, so small
    fee differences never pile up. The halt reason gives no dollar amounts (the log is public)."""
    a = st.get("audit")
    if not a or a.get("since") != live_since:
        a = st["audit"] = {"since": live_since, "snap": None, "bad": 0, "halt": None}
    if a["halt"] or st.get("open"):
        return
    if any(str(o.get("client_order_id", "")).startswith("r21-") for o in api.resting()) or api.positions():
        return
    bal, cum = api.balance_usd(), float(sum(p for _, p in pnls))
    if a["snap"] is None:
        a["snap"] = {"bal": bal, "cum": cum}
        return
    expected = a["snap"]["bal"] + (cum - a["snap"]["cum"])
    if abs(bal - expected) <= max(1.0, 0.01 * a["snap"]["bal"]):
        a["snap"], a["bad"] = {"bal": bal, "cum": cum}, 0
        return
    a["bad"] += 1
    if a["bad"] >= AUDIT_CHECKS:
        off = (bal - expected) / max(expected, 1e-9)
        a["halt"] = f"cash moved {off:+.1%} more than the settlement records explain (deposit/withdrawal? unknown trade?)"


def record_result(st: dict, now: float, pnl: float) -> None:
    """Apply the pause/half-size/daily-stop rules to a settled market's P&L."""
    st["results"].append({"t": now, "pnl": pnl})
    if pnl < 0:
        st["day_loss"] += -pnl
        st["pause_until"] = now + PAUSE_HOURS * 3600
        st["half_until"] = st["pause_until"] + HALF_DAYS * 86400


# ---------------------------------------------------------------------- loop
def log(mode: str, event: str, ticker="", side="", count=0, z=np.nan, spot=np.nan, balance=np.nan, detail=""):
    if mode == "LIVE" or os.environ.get("KALSHI_KEY_ID"):
        balance = np.nan  # the log is committed to a public repository: never write a real account balance
    row = dict(time_utc=pd.Timestamp.now(tz="UTC").isoformat(), mode=mode, event=event, ticker=ticker, side=side,
               count=count, z=z, spot=spot, balance=balance, detail=str(detail)[:300])
    pd.DataFrame([row])[LOG_COLS].to_csv(LOG, mode="a", header=not (LOG.exists() and LOG.stat().st_size), index=False)
    print(f"{row['time_utc'][:19]} {mode} {event} {ticker} {side} {count} {detail}", flush=True)


def candidates(now: pd.Timestamp) -> list:
    """Every 15-minute market to bid on right now: the Round 25 gate on the smallest lead any of the three
    exchanges shows (edge/prices.py), and only when at least two are fresh and they agree."""
    out = []
    for series in SERIES:
        spots, v, _ = px.quote(sig.SERIES[series], now)
        if not spots:
            continue
        s = float(np.median(spots))
        for m in sig.open_markets(series, now):
            zy, zn = px.worst_z(sig.z_sides, spots, v, m.get("strike_type"), m.get("floor_strike"), m.get("cap_strike"),
                                m["_close"], now)
            tau = max((m["_close"] - now).total_seconds() / 60, 0.5)
            for side, z in (("yes", zy), ("no", zn)):
                if np.isfinite(z) and z > 0 and flip_risk(z, tau) < P_MAX:
                    out.append((m, series, side, z, s))
    return out


def decide(now: pd.Timestamp):
    """The paper bot bids on all of them; with one position at a time we take the one with the shortest queue
    at 99c ahead of us, since that is the one most likely to fill (paper data: most fills had < 1k ahead)."""
    best, best_q = None, math.inf
    for c in candidates(now):
        q = sig.queue_ahead(c[0]["ticker"], c[2])
        q = q if np.isfinite(q) else math.inf
        if best is None or q < best_q:
            best, best_q = c, q
    return None if best is None else (*best, best_q)


def still_decided(o: dict, now: pd.Timestamp) -> bool:
    spots, v, _ = px.quote(sig.SERIES[o["series"]], now)
    if not spots:
        return False  # stale or disagreeing data: treat as not decided, so the order is pulled
    zy, zn = px.worst_z(sig.z_sides, spots, v, o["strike_type"], o["floor"], o["cap"], pd.Timestamp(o["close"]), now)
    z = zy if o["side"] == "yes" else zn
    tau = max((pd.Timestamp(o["close"]) - now).total_seconds() / 60, 0.5)
    return bool(np.isfinite(z) and z > 0 and flip_risk(z, tau) < P_MAX)


def settle(api: Kalshi, st: dict, mode: str, now: pd.Timestamp) -> None:
    """After the open market closes, read its result and our fill, and apply the risk rules."""
    o = st["open"]
    if not o or now < pd.Timestamp(o["close"]) + pd.Timedelta(minutes=2):
        return
    r = sig.wx._get(f"{sig.wx.KALSHI}/markets/{o['ticker']}")
    m = r.json().get("market", {}) if r is not None and r.status_code == 200 else {}
    if m.get("result") not in ("yes", "no"):
        if now > pd.Timestamp(o["close"]) + pd.Timedelta(hours=3):  # void or stuck: unblock, risk comes from settlements
            log(mode, "settled", o["ticker"], o["side"], 0, detail=f"result={m.get('result')!r} unresolved after 3h pnl=0.00")
            st["open"] = None
        return
    if mode == "LIVE" and api.authed:
        filled = api.filled(o["ticker"], o.get("order_id"))
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
        if not still_decided(o, now) or STOP.exists() or st.get("control_stop") or st.get("gov_halt"):
            if mode == "LIVE" and o.get("order_id"):
                api.cancel(o["order_id"], o.get("ticker"))
            log(mode, "cancel", o["ticker"], o["side"], o["count"], detail="z below threshold, stale data or stop")
            o["cancelled"] = True
            o["cancelled_at"] = now.isoformat()
        return
    if o:
        return  # closed, waiting for its result
    why = blocked(st, now.timestamp(), balance)
    if why:
        return
    if mode == "LIVE" and api.positions():
        return  # a position from an earlier job is still open: wait until it settles
    pick = decide(now)
    if not pick:
        return
    m, series, side, z, spot, q = pick
    if st.get("cooldown", {}).get(m["ticker"], 0) > now.timestamp():
        return  # this market just rejected our order; let the book change first
    if m["ticker"] in st.get("traded", []) or m["_close"] <= now:
        return  # never a second order on a market already traded, and never one on a closed market
    p = flip_risk(z, max((m["_close"] - now).total_seconds() / 60, 0.5))
    frac = min(st.get("stake_fraction", 0.5), kelly(p))  # Round 25 sizing, never above Claude's stake cap
    count = size_for(balance, st, now.timestamp(), frac, st.get("max_contracts"))
    if count < 1:
        log(mode, "skip", m["ticker"], side, 0, z, spot, balance, "balance too small")
        return
    st["traded"] = (st.get("traded", []) + [m["ticker"]])[-500:]
    st["open"] = dict(ticker=m["ticker"], series=series, side=side, count=count, close=m["_close"].isoformat(),
                      strike_type=m.get("strike_type"), floor=m.get("floor_strike"), cap=m.get("cap_strike"),
                      order_id=None, placed=now.isoformat(), queue_ahead=(q if np.isfinite(q) else None))
    if mode == "LIVE":
        try:
            order = api.buy(m["ticker"], side, count, expires=m["_close"].timestamp())
        except Exception:
            st["open"] = None  # rejected (e.g. post-only would cross): nothing rests
            st["traded"] = [t for t in st["traded"] if t != m["ticker"]]  # a rejected order is not a trade
            st.setdefault("cooldown", {})[m["ticker"]] = now.timestamp() + 60
            raise
        st["open"]["order_id"] = order.get("order_id")
        save_state(st)  # tracked before anything else can fail
    log(mode, "place", m["ticker"], side, count, round(z, 2), spot, balance,
        f"queue_ahead={q:.0f} risk={p:.5f} frac={frac:.3f} " + json.dumps(order_body(m["ticker"], side, count)))


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


def sweep_strays(api: Kalshi, st: dict, mode: str) -> None:
    """Cancel any resting order of ours that is not the one we are tracking."""
    keep = (st.get("open") or {}).get("order_id")
    for o in api.resting():
        if str(o.get("client_order_id", "")).startswith("r21-") and o.get("order_id") != keep:
            api.cancel(o["order_id"], o.get("ticker"))
            log(mode, "cancel", o.get("ticker", ""), detail="stray order")


def rebuild_risk(api: Kalshi, st: dict, now: float) -> None:
    """Re-apply the loss rules from Kalshi's own settlement records (the source of truth in LIVE): the pause and
    half size after any losing market, and today's realised loss for the daily stop. Run at start and every
    minute, so a loss on a position left by an earlier job is never missed."""
    day_start = math.floor(now / 86400) * 86400
    day_loss = 0.0
    for t, pnl in api.recent_settlement_pnls(now - (PAUSE_HOURS * 3600 + HALF_DAYS * 86400)):
        if pnl < 0:
            st["pause_until"] = max(st["pause_until"], t + PAUSE_HOURS * 3600)
            st["half_until"] = max(st["half_until"], t + PAUSE_HOURS * 3600 + HALF_DAYS * 86400)
            if t >= day_start:
                day_loss += -pnl
    st["day_loss"] = max(st["day_loss"], day_loss)


def commit_logs() -> None:
    files = [str(p.relative_to(ROOT.parent)) for p in (LOG, STATE, ROOT / "LIVE21.md") if p.exists()]
    if not _git(["add", *files]) or not _git(["commit", "-q", "-m", "live21: log [skip ci]"]):
        return
    if not _git(["pull", "--rebase", "-q"], timeout=90):
        _git(["rebase", "--abort"])  # never leave the checkout mid-rebase; the next commit tries again
        return
    _git(["push", "-q"], timeout=90)


def run():
    key_id, pem = os.environ.get("KALSHI_KEY_ID"), os.environ.get("KALSHI_PRIVATE_KEY")
    api = Kalshi(key_id, pem)
    st = load_state()
    control = read_control()
    apply_control(st, control)
    govern(api, st, control, time.time())
    mode = "LIVE" if live_allowed(api, control) and not st.get("gov_halt") else "DRY"
    log(mode, "start", detail=f"authed={api.authed} max={MAX_CONTRACTS} series={','.join(SERIES)}")
    if mode == "LIVE":
        st["open"] = None
        sweep_strays(api, st, mode)  # clean slate: nothing of ours rests from a previous job
        rebuild_risk(api, st, time.time())
        save_state(st)
    import signal

    def stop_signal(signum, frame):  # GitHub cancels a job with SIGINT/SIGTERM: leave nothing resting
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop_signal)
    t0, last_sweep, last_commit = time.time(), 0.0, time.time()
    seconds = int(os.environ.get("LIVE21_SECONDS", 20700))
    try:
        loop(api, st, mode, t0, seconds, last_sweep, last_commit)
    finally:
        if api.authed:  # whatever mode we ended in, nothing of ours stays resting
            try:
                for o in api.resting():
                    if str(o.get("client_order_id", "")).startswith("r21-"):
                        api.cancel(o["order_id"], o.get("ticker"))
                        log(mode, "cancel", o.get("ticker", ""), detail="job ending: nothing left resting")
            except Exception as e:
                log(mode, "error", detail=f"exit cancel: {e!r}")
        save_state(st)
        log(mode, "stop", detail="job ending")
        (ROOT / "LIVE21.md").write_text(summary())


def apply_control(st: dict, control: dict) -> None:
    st["stake_fraction"], st["max_contracts"], st["control_stop"] = (
        control["stake_fraction"], control["max_contracts"], control["stop"])


def go_dry(api, st) -> None:
    """Leaving LIVE mid-run: pull every resting order of ours first."""
    for o in api.resting():
        if str(o.get("client_order_id", "")).startswith("r21-"):
            api.cancel(o["order_id"], o.get("ticker"))
            log("LIVE", "cancel", o.get("ticker", ""), detail="switching to DRY")
    st["open"] = None


def loop(api, st, mode, t0, seconds, last_sweep, last_commit):
    last_risk, last_control = 0.0, time.time()
    while time.time() - t0 < seconds:
        now = pd.Timestamp.now(tz="UTC")
        if time.time() - last_control > 60:  # Claude's control file, from GitHub
            try:
                control = read_control()
                apply_control(st, control)
                govern(api, st, control, time.time())
                want = "LIVE" if live_allowed(api, control) and not st.get("gov_halt") else "DRY"
                if want != mode:
                    if mode == "LIVE":
                        go_dry(api, st)
                    else:
                        st["open"] = None
                        sweep_strays(api, st, "LIVE")
                        rebuild_risk(api, st, time.time())
                    log(want, "mode", detail=f"{mode} -> {want} ({st.get('gov_halt') or 'control file'})")
                    mode = want
            except Exception as e:
                log(mode, "error", detail=f"control: {e!r}")
            last_control = time.time()
        try:
            step(api, st, mode, now)
        except Exception as e:  # never die silently with an order resting: log, pull orders, carry on
            log(mode, "error", detail=repr(e))
            if mode == "LIVE" and st.get("open") and st["open"].get("order_id"):
                try:
                    api.cancel(st["open"]["order_id"], st["open"].get("ticker"))
                except Exception:
                    pass
        if mode == "LIVE" and time.time() - last_risk > 60:
            try:
                rebuild_risk(api, st, time.time())
            except Exception as e:
                log(mode, "error", detail=f"risk rebuild: {e!r}")
            last_risk = time.time()
        if mode == "LIVE" and time.time() - last_sweep > 30:
            try:
                sweep_strays(api, st, mode)
            except Exception as e:
                log(mode, "error", detail=f"sweep: {e!r}")
            last_sweep = time.time()
        save_state(st)
        if time.time() - last_commit > 900:  # state survives a crashed job
            (ROOT / "LIVE21.md").write_text(summary())
            if os.environ.get("GITHUB_ACTIONS") == "true":
                commit_logs()
            last_commit = time.time()
        time.sleep(max(0.0, 5 - (time.time() - now.timestamp())))


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
    for side in ("yes", "no"):  # a 1c post-only bid is rejected only if it would cross; then try the other side
        try:
            order = api.buy(m["ticker"], side, 1, cents=1)
            break
        except RuntimeError as e:
            print(f"{side} at 1c rejected: {e}")
    else:
        raise SystemExit("both sides rejected: check the error text above")
    print(f"placed test order {order.get('order_id')} on {m['ticker']}: status {order.get('status')}")
    ids = [o.get("order_id") for o in api.resting()]
    print("resting:", order.get("order_id") in ids)
    api.cancel(order["order_id"], m["ticker"])
    print("positions:", len(api.positions()), "| recent settlements read:", len(api.recent_settlement_pnls(time.time() - 86400 * 30)))
    print("cancelled; selftest OK")


if __name__ == "__main__":
    import sys
    selftest() if sys.argv[1:] == ["selftest"] else run()
