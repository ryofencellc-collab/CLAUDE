"""Round 39 collector: free Cboe delayed option quotes (~15 min delay) for 0DTE / 1-3DTE.

No account needed. Every POLL seconds during US hours it pulls the full SPX (incl. SPXW
dailies) and SPY chains, keeps expiries within MAX_DTE calendar days and strikes within
BAND of spot, and writes one gzipped CSV per (day, symbol, job) under data/odte/.
These snapshots are the dataset the PROTOCOL_ROUND39 strategies are scored on.
"""
from __future__ import annotations
import gzip, io, os, re, subprocess, time
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "odte")
URL = "https://cdn.cboe.com/api/global/delayed_quotes/options/{}.json"
SYMBOLS = {"SPX": "_SPX", "SPY": "SPY", "QQQ": "QQQ", "IWM": "IWM"}          # daily 0DTE expiries
FRIDAY = {s: s for s in ("AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA")}  # weekly options: 0DTE on Fridays (Round 64 universe)


def symbols_today(now: datetime) -> dict:
    return {**SYMBOLS, **FRIDAY} if now.astimezone(timezone(timedelta(hours=-5))).weekday() == 4 else dict(SYMBOLS)
POLL = int(os.environ.get("ODTE_POLL", "60"))
MAX_DTE = 3
BAND = 0.04
STOP_UTC = os.environ.get("ODTE_STOP_UTC", "21:20")
START_UTC = os.environ.get("ODTE_START_UTC") or "12:50"
WAIT_MAX = 5 * 3600 + 30 * 60
MAX_SECONDS = int(os.environ.get("ODTE_MAX_SECONDS", str(5 * 3600 + 40 * 60)))
SYM = re.compile(r"^([A-Z]+?)(\d{6})([CP])(\d{8})$")
KEEP = ["bid", "ask", "bid_size", "ask_size", "iv", "delta", "gamma", "theo",
        "volume", "open_interest", "last_trade_price", "last_trade_time"]


def parse(js: dict, fetched: datetime) -> pd.DataFrame:
    """Flatten one Cboe chain payload into near-dated, near-the-money rows."""
    d = js.get("data", {})
    spot = d.get("current_price") or d.get("close")
    if not spot:
        return pd.DataFrame()
    today = fetched.astimezone(timezone(timedelta(hours=-5))).date()  # ET (EST); DTE only filters
    rows = []
    for o in d.get("options", []):
        m = SYM.match(o.get("option", ""))
        if not m:
            continue
        root, ymd, cp, k = m.groups()
        exp = datetime.strptime(ymd, "%y%m%d").date()
        strike = int(k) / 1000
        if not (0 <= (exp - today).days <= MAX_DTE) or abs(strike / spot - 1) > BAND:
            continue
        rows.append({"root": root, "exp": exp.isoformat(), "cp": cp, "K": strike,
                     **{c: o.get(c) for c in KEEP}})
    df = pd.DataFrame(rows)
    if len(df):
        df.insert(0, "spot", spot)
        df.insert(0, "ts_fetch", fetched.strftime("%Y-%m-%dT%H:%M:%SZ"))
        df.insert(0, "ts_feed", js.get("timestamp"))
    return df


def fetch(sym: str) -> dict:
    r = requests.get(URL.format({**SYMBOLS, **FRIDAY}[sym]), timeout=40,
                     headers={"User-Agent": "Mozilla/5.0 (research collector)"})
    r.raise_for_status()
    return r.json()


YAHOO = {"SPX": "^SPX"}
YPOLL = int(os.environ.get("ODTE_YPOLL", "300"))
OUT_Y = os.path.join(ROOT, "data", "odte_y")   # Yahoo fallback (different feed timing): kept apart from the Cboe record


def _bs(S, K, T, iv, cp, r=0.04):
    """Black-Scholes delta, gamma, theo (Yahoo gives no Greeks)."""
    import math
    if not (S > 0 and K > 0 and T > 0 and iv and iv > 0): return (float("nan"),) * 3
    v = iv * math.sqrt(T); d1 = (math.log(S / K) + (r + iv * iv / 2) * T) / v; d2 = d1 - v
    N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2))); n = math.exp(-d1 * d1 / 2) / math.sqrt(2 * math.pi)
    df = math.exp(-r * T)
    if cp == "C": return N(d1), n / (S * v), S * N(d1) - K * df * N(d2)
    return N(d1) - 1, n / (S * v), K * df * N(-d2) - S * N(-d1)


def _iv(S, K, T, price, cp):
    """Implied vol from the mid by bisection (Yahoo's own IV is unreliable away from the money)."""
    import math
    intrinsic = max(S - K, 0) if cp == "C" else max(K - S, 0)
    if not (price == price and price > intrinsic * 0.999 and T > 0): return float("nan")
    lo, hi = 1e-3, 5.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if _bs(S, K, T, mid, cp)[2] > price: hi = mid
        else: lo = mid
    return (lo + hi) / 2


def yahoo_chain(sym: str, fetched: datetime) -> pd.DataFrame:
    """Same schema as parse(), from Yahoo option chains (expiries within MAX_DTE, strikes within BAND)."""
    import yfinance as yf
    t = yf.Ticker(YAHOO.get(sym, sym))
    spot = float(t.fast_info["last_price"])
    et = fetched.astimezone(timezone(timedelta(hours=-5))); today = et.date()
    rows = []
    for e in t.options:
        exp = datetime.strptime(e, "%Y-%m-%d").date()
        if not (0 <= (exp - today).days <= MAX_DTE): continue
        close = datetime(exp.year, exp.month, exp.day, 16, 0, tzinfo=timezone(timedelta(hours=-5)))
        T = max((close - et).total_seconds(), 60) / (365 * 86400)
        ch = t.option_chain(e)
        # Yahoo's option quotes lag its spot: use the parity-implied underlying (C - P + K, median of the 5 strikes nearest spot)
        mc = ch.calls.set_index("strike"); mp = ch.puts.set_index("strike")
        ks = [k for k in mc.index.intersection(mp.index) if mc.bid[k] > 0 and mp.bid[k] > 0 and mc.ask[k] >= mc.bid[k] and mp.ask[k] >= mp.bid[k]]
        ks = sorted(ks, key=lambda k: abs(k - spot))[:5]
        S = float(np.median([(mc.bid[k] + mc.ask[k]) / 2 - (mp.bid[k] + mp.ask[k]) / 2 + k for k in ks])) if ks else float("nan")
        for cp, df in (("C", ch.calls), ("P", ch.puts)):
            df = df[(df.strike / spot - 1).abs() <= BAND]
            for o in df.itertuples():
                m = SYM.match(o.contractSymbol)
                mid = (o.bid + o.ask) / 2 if o.bid > 0 and o.ask >= o.bid else float("nan")
                iv = _iv(S, o.strike, T, mid, cp)
                d, g, th = _bs(S, o.strike, T, iv, cp)
                rows.append({"root": m.group(1) if m else sym, "exp": exp.isoformat(), "spot_parity": S, "cp": cp, "K": float(o.strike), "bid": o.bid, "ask": o.ask,
                             "bid_size": None, "ask_size": None, "iv": iv, "iv_yahoo": o.impliedVolatility, "delta": d, "gamma": g, "theo": th,
                             "volume": o.volume, "open_interest": o.openInterest, "last_trade_price": o.lastPrice,
                             "last_trade_time": o.lastTradeDate.isoformat() if pd.notna(o.lastTradeDate) else None})
    out = pd.DataFrame(rows)
    if len(out):
        out.insert(0, "spot", spot); out.insert(0, "ts_fetch", fetched.strftime("%Y-%m-%dT%H:%M:%SZ")); out.insert(0, "ts_feed", "yahoo")
    return out


def write(frames: dict, day: str, tag: str, out: str = OUT) -> list[str]:
    paths = []
    for sym, parts in frames.items():
        if not parts:
            continue
        p = os.path.join(out, day, f"{sym}_{tag}.csv.gz")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        buf = io.StringIO()
        pd.concat(parts, ignore_index=True).to_csv(buf, index=False)
        with gzip.open(p, "wt") as fh:
            fh.write(buf.getvalue())
        paths.append(p)
    return paths


def commit(paths: list[str], msg: str) -> None:
    if not paths:
        return
    for c in (["git", "add", "-f", *paths], ["git", "commit", "-q", "-m", msg],
              ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]):
        try:
            if subprocess.run(c, cwd=ROOT, timeout=180).returncode != 0 and c[1] == "commit":
                return
        except subprocess.TimeoutExpired:
            return


def _at(day: datetime, hhmm: str) -> datetime:
    hh, mm = map(int, hhmm.split(":"))
    return day.replace(hour=hh, minute=mm, second=0, microsecond=0)


def next_window(now: datetime) -> tuple[datetime, datetime]:
    """The collection window [start, stop) that is open now, or the next one (weekdays only)."""
    d = now
    for _ in range(8):
        a, b = _at(d, START_UTC), _at(d, STOP_UTC)
        if d.weekday() < 5 and now < b:
            return a, b
        d = (d + timedelta(days=1)).replace(hour=0, minute=0)
    raise RuntimeError("no window within a week")


def run() -> None:
    now = datetime.now(timezone.utc)
    a, b = next_window(now)
    if now < a:  # outside market hours: wait (at most ~5.5 h per job), then let the workflow start the next link
        wait = min((a - now).total_seconds(), WAIT_MAX)
        print(f"{now:%a %H:%M}Z: next window {a:%a %H:%M}Z, waiting {wait / 60:.0f} min", flush=True)
        time.sleep(wait)
        return
    collect()


def collect() -> None:
    t0 = time.time()
    start = datetime.now(timezone.utc)
    day, tag = start.strftime("%Y-%m-%d"), start.strftime("%H%M")
    hh, mm = map(int, STOP_UTC.split(":"))
    stop = start.replace(hour=hh, minute=mm, second=0, microsecond=0)
    syms = symbols_today(start)
    frames = {s: [] for s in syms}
    yframes = {s: [] for s in syms}; cboe_down = set(); y_next = {s: 0.0 for s in syms}
    last_feed = {s: None for s in syms}
    last_commit = time.time()
    while time.time() - t0 < MAX_SECONDS and datetime.now(timezone.utc) < stop:
        now = datetime.now(timezone.utc)
        for s in syms:
            try:
                js = fetch(s)
                if js.get("timestamp") == last_feed[s]:
                    continue
                last_feed[s] = js.get("timestamp")
                df = parse(js, now)
                frames[s].append(df)
                print(f"{now:%H:%M:%S} {s} feed={last_feed[s]} rows={len(df)}", flush=True)
            except Exception as e:
                print(f"{now:%H:%M:%S} {s} failed: {e!r}", flush=True)
                if "403" in repr(e): cboe_down.add(s)
            if s in cboe_down and time.time() >= y_next[s]:   # Cboe refuses this host: record Yahoo instead (separate folder), never work around the block
                y_next[s] = time.time() + YPOLL                  # Yahoo: one chain per symbol every 5 min; back off 15 min if it rate-limits
                try:
                    df = yahoo_chain(s, now)
                    if len(df): yframes[s].append(df)
                    print(f"{now:%H:%M:%S} {s} yahoo rows={len(df)}", flush=True)
                except Exception as e:
                    print(f"{now:%H:%M:%S} {s} yahoo failed: {e!r}", flush=True)
                    if "429" in repr(e) or "Rate" in repr(e): y_next[s] = time.time() + 900
        if os.environ.get("ODTE_COMMIT") == "1" and time.time() - last_commit > 1800:
            commit(write(frames, day, tag) + write(yframes, day, tag, OUT_Y), f"odte: snapshots {day} {now:%H:%M}Z [skip ci]")
            last_commit = time.time()
        time.sleep(max(0.0, POLL - (time.time() - now.timestamp())))
    paths = write(frames, day, tag) + write(yframes, day, tag, OUT_Y)
    if os.environ.get("ODTE_COMMIT") == "1":
        commit(paths, f"odte: snapshots {day} final [skip ci]")


if __name__ == "__main__":
    run()
