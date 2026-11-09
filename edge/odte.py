"""Round 39 collector: free Cboe delayed option quotes (~15 min delay) for 0DTE / 1-3DTE.

No account needed. Every POLL seconds during US hours it pulls the full SPX (incl. SPXW
dailies) and SPY chains, keeps expiries within MAX_DTE calendar days and strikes within
BAND of spot, and writes one gzipped CSV per (day, symbol, job) under data/odte/.
These snapshots are the dataset the PROTOCOL_ROUND39 strategies are scored on.
"""
from __future__ import annotations
import gzip, io, os, re, subprocess, time
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "odte")
URL = "https://cdn.cboe.com/api/global/delayed_quotes/options/{}.json"
SYMBOLS = {"SPX": "_SPX", "SPY": "SPY"}
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
    r = requests.get(URL.format(SYMBOLS[sym]), timeout=40,
                     headers={"User-Agent": "Mozilla/5.0 (research collector)"})
    r.raise_for_status()
    return r.json()


def write(frames: dict, day: str, tag: str) -> list[str]:
    paths = []
    for sym, parts in frames.items():
        if not parts:
            continue
        p = os.path.join(OUT, day, f"{sym}_{tag}.csv.gz")
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
    frames = {s: [] for s in SYMBOLS}
    last_feed = {s: None for s in SYMBOLS}
    last_commit = time.time()
    while time.time() - t0 < MAX_SECONDS and datetime.now(timezone.utc) < stop:
        now = datetime.now(timezone.utc)
        for s in SYMBOLS:
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
        if os.environ.get("ODTE_COMMIT") == "1" and time.time() - last_commit > 1800:
            commit(write(frames, day, tag), f"odte: snapshots {day} {now:%H:%M}Z [skip ci]")
            last_commit = time.time()
        time.sleep(max(0.0, POLL - (time.time() - now.timestamp())))
    paths = write(frames, day, tag)
    if os.environ.get("ODTE_COMMIT") == "1":
        commit(paths, f"odte: snapshots {day} final [skip ci]")


if __name__ == "__main__":
    run()
