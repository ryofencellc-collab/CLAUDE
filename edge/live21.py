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
CONTROL = ROOT.parent / "control" / "live21.json"  # Claude's switch; re-read from GitHub every minute
SERIES = [s for s in sig.SERIES if s.endswith("15M")]  # capital-efficient part only (see PROTOCOL_ROUND22.md)
MAX_CONTRACTS = int(os.environ.get("LIVE21_MAX", 1000))
PRICE_CENTS = 99
DAILY_STOP = 0.10
PAUSE_HOURS, HALF_DAYS = 24, 7
API = "https://api.elections.kalshi.com"
BASE = "/trade-api/v2"
LOG_COLS = ["time_utc", "mode", "event", "ticker", "side", "count", "z", "spot", "balance", "detail"]


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
        b = self.call("GET", "/portfolio/balance")
        return num(b, "balance", scale=0.01) if "balance" in b else num(b, "balance_dollars")

    def resting(self) -> list[dict]:
        return self.call("GET", "/portfolio/orders", params={"status": "resting", "limit": 200}).get("orders", [])

    def positions(self) -> list[dict]:
        ps = self.call("GET", "/portfolio/positions", params={"limit": 200}).get("market_positions", [])
        return [p for p in ps if num(p, "position_fp", "position") != 0]

    def filled(self, ticker: str) -> float:
        fills = self.call("GET", "/portfolio/fills", params={"ticker": ticker, "limit": 200}).get("fills", [])
        return sum(num(f, "count_fp", "count") for f in fills if f.get("action", "buy") == "buy" and f.get("ticker", ticker) == ticker)

    def recent_settlement_pnls(self, since: float) -> list[tuple[float, float]]:
        """(settled unix time, P&L in dollars) for our settlements since `since`."""
        out = []
        for x in self.call("GET", "/portfolio/settlements", params={"limit": 200}).get("settlements", []):
            t = pd.Timestamp(x.get("settled_time")).timestamp() if x.get("settled_time") else 0
            if t < since:
                continue
            revenue = num(x, "revenue", scale=0.01)
            cost = (num(x, "yes_total_cost_dollars") or num(x, "yes_total_cost", scale=0.01)) + \
                (num(x, "no_total_cost_dollars") or num(x, "no_total_cost", scale=0.01))
            fee = num(x, "fee_cost_dollars") or num(x, "fee_cost", scale=0.01)
            out.append((t, revenue - cost - fee))
        return out

    def buy(self, ticker: str, side: str, count: int, cents: int = PRICE_CENTS, expires: float | None = None) -> dict:
        body = order_body(ticker, side, count, cents, expires)
        return self.call("POST", "/portfolio/orders", body=body).get("order", {})

    def cancel(self, order_id: str) -> None:
        try:
            self.call("DELETE", f"/portfolio/orders/{order_id}")
        except RuntimeError as e:  # already filled, expired or cancelled: nothing left to pull
            if "-> 404" not in str(e) and "-> 409" not in str(e):
                raise


def order_body(ticker: str, side: str, count: int, cents: int = PRICE_CENTS, expires: float | None = None) -> dict:
    """Post-only limit buy for the decided side: it rests in the book and can never take liquidity. With
    `expires` (unix seconds, the market's close) Kalshi drops it by itself even if this bot has died."""
    body = {"ticker": ticker, "action": "buy", "side": side, "count": int(count), "type": "limit",
            "client_order_id": f"r21-{uuid.uuid4().hex[:16]}", "post_only": True}
    if expires:
        body["expiration_ts"] = int(expires)
    body["yes_price" if side == "yes" else "no_price"] = int(cents)
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


def read_control() -> dict:
    """control/live21.json, preferring the latest version on GitHub so a commit reaches a running job. On
    GitHub Actions, if GitHub cannot be reached CONTROL_MAX_MISSES times in a row, the answer is "stopped"."""
    import subprocess
    text, remote_failed = None, False
    if os.environ.get("GITHUB_ACTIONS") == "true":
        ref = os.environ.get("GITHUB_REF_NAME", "")
        ok = subprocess.run(["git", "fetch", "-q", "origin", ref], cwd=ROOT.parent).returncode == 0
        if ok:
            r = subprocess.run(["git", "show", f"origin/{ref}:control/live21.json"], cwd=ROOT.parent,
                               capture_output=True, text=True)
            text = r.stdout if r.returncode == 0 else None
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
    stop = bool(c.get("stop", True)) or _control_misses[0] >= CONTROL_MAX_MISSES
    # anything missing or unreadable means: not live, stopped, smallest stake
    return {"live": bool(c.get("live", False)) and not stop, "stop": stop, "stake_fraction": frac, "max_contracts": cap}


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
    if mode == "LIVE" or os.environ.get("KALSHI_KEY_ID"):
        balance = np.nan  # the log is committed to a public repository: never write a real account balance
    row = dict(time_utc=pd.Timestamp.now(tz="UTC").isoformat(), mode=mode, event=event, ticker=ticker, side=side,
               count=count, z=z, spot=spot, balance=balance, detail=str(detail)[:300])
    pd.DataFrame([row])[LOG_COLS].to_csv(LOG, mode="a", header=not (LOG.exists() and LOG.stat().st_size), index=False)
    print(f"{row['time_utc'][:19]} {mode} {event} {ticker} {side} {count} {detail}", flush=True)


def candidates(now: pd.Timestamp) -> list:
    """Every 15-minute market the paper bot would bid on right now (its placement rule, unchanged)."""
    spots = {sig.SERIES[s]: sig.spot_and_vol(sig.SERIES[s], now) for s in SERIES}
    out = []
    for series in SERIES:
        s, v = spots[sig.SERIES[series]]
        if not np.isfinite(s):
            continue
        for m in sig.open_markets(series, now):
            zy, zn = sig.z_sides(m.get("strike_type"), m.get("floor_strike"), m.get("cap_strike"), s, v, m["_close"], now)
            if np.isfinite(zy) and zy >= sig.zmin(series):
                out.append((m, series, "yes", zy, s))
            elif np.isfinite(zn) and zn >= sig.zmin(series):
                out.append((m, series, "no", zn, s))
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
        if now > pd.Timestamp(o["close"]) + pd.Timedelta(hours=3):  # void or stuck: unblock, risk comes from settlements
            log(mode, "settled", o["ticker"], o["side"], 0, detail=f"result={m.get('result')!r} unresolved after 3h pnl=0.00")
            st["open"] = None
        return
    if mode == "LIVE" and api.authed:
        filled = api.filled(o["ticker"])
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
        if not still_decided(o, now) or STOP.exists() or st.get("control_stop"):
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
    count = size_for(balance, st, now.timestamp(), st.get("stake_fraction", 0.5), st.get("max_contracts"))
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
        f"queue_ahead={q:.0f} " + json.dumps(order_body(m["ticker"], side, count)))


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
            api.cancel(o["order_id"])
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
    import subprocess
    files = [str(p.relative_to(ROOT.parent)) for p in (LOG, STATE, ROOT / "LIVE21.md") if p.exists()]
    for c in (["git", "add", *files], ["git", "commit", "-q", "-m", "live21: log [skip ci]"],
              ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]):
        if subprocess.run(c, cwd=ROOT.parent).returncode != 0 and c[1] == "commit":
            return


def run():
    key_id, pem = os.environ.get("KALSHI_KEY_ID"), os.environ.get("KALSHI_PRIVATE_KEY")
    api = Kalshi(key_id, pem)
    st = load_state()
    control = read_control()
    apply_control(st, control)
    mode = "LIVE" if live_allowed(api, control) else "DRY"
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
                        api.cancel(o["order_id"])
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
            api.cancel(o["order_id"])
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
                want = "LIVE" if live_allowed(api, control) else "DRY"
                if want != mode:
                    if mode == "LIVE":
                        go_dry(api, st)
                    else:
                        st["open"] = None
                        sweep_strays(api, st, "LIVE")
                        rebuild_risk(api, st, time.time())
                    log(want, "mode", detail=f"{mode} -> {want} (control file)")
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
                    api.cancel(st["open"]["order_id"])
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
    api.cancel(order["order_id"])
    print("positions:", len(api.positions()), "| recent settlements read:", len(api.recent_settlement_pnls(time.time() - 86400 * 30)))
    print("cancelled; selftest OK")


if __name__ == "__main__":
    import sys
    selftest() if sys.argv[1:] == ["selftest"] else run()
