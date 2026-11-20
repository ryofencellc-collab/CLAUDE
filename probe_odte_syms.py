"""Diagnose the 2026-11-20 collector: Cboe status and Yahoo fallback from a GitHub runner."""
import time
from datetime import datetime, timezone
from edge import odte as o
for s in ["SPY", "SPX", "QQQ", "AAPL"]:
    t = time.time()
    try:
        o.fetch(s); print(s, "cboe OK", flush=True)
    except Exception as e:
        print(s, "cboe", repr(e)[:120], flush=True)
    try:
        d = o.yahoo_chain(s, datetime.now(timezone.utc)); print(s, "yahoo rows", len(d), f"{time.time() - t:.1f}s", flush=True)
    except Exception as e:
        print(s, "yahoo FAILED", repr(e)[:300], flush=True)
