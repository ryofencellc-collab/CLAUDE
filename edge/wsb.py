"""Round 50 collector: ApeWisdom Reddit ticker-mention snapshots, hourly (PROTOCOL_ROUND50.md)."""
from __future__ import annotations
import os, subprocess, time
from datetime import datetime, timezone
import pandas as pd, requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "wsb")
API = "https://apewisdom.io/api/v1.0/filter/{}/page/{}"
FILTERS = ("all-stocks", "wallstreetbets")
RUN_SECONDS = int(os.environ.get("WSB_SECONDS", str(5 * 3600 + 40 * 60)))
EVERY = 3600


def snapshot(now: datetime) -> pd.DataFrame:
    s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (research)"
    rows = []
    for f in FILTERS:
        for page in range(1, 30):
            try:
                j = s.get(API.format(f, page), timeout=30).json()
            except Exception as e:
                print(f"{f} p{page} failed: {e!r}", flush=True); break
            for r in j.get("results", []):
                rows.append({"ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "filter": f, **r})
            if page >= int(j.get("pages") or 1):
                break
            time.sleep(1)
    return pd.DataFrame(rows)


def run():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    while time.time() - t0 < RUN_SECONDS:
        now = datetime.now(timezone.utc)
        d = snapshot(now)
        if len(d):
            p = os.path.join(OUT, f"{now:%Y-%m-%d}.csv.gz")
            d.to_csv(p, mode="a", header=not os.path.exists(p), index=False, compression="gzip")
            print(f"{now:%H:%M} saved {len(d)} rows", flush=True)
            if os.environ.get("WSB_COMMIT") == "1":
                for c in (["git", "add", "-f", p], ["git", "commit", "-q", "-m", f"wsb: snapshot {now:%Y-%m-%dT%H:%MZ} [skip ci]"],
                          ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]):
                    try:
                        if subprocess.run(c, cwd=ROOT, timeout=120).returncode != 0 and c[1] == "commit":
                            break
                    except subprocess.TimeoutExpired:
                        break
        time.sleep(max(0.0, EVERY - (time.time() - now.timestamp())))


if __name__ == "__main__":
    run()
