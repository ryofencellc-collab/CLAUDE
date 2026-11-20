"""Time Cboe fetch + parse for every collector symbol (diagnose the 2026-11-20 stall)."""
import time
from datetime import datetime, timezone
from edge import odte as o
for s in {**o.SYMBOLS, **o.FRIDAY}:
    t = time.time()
    try:
        js = o.fetch(s); t1 = time.time()
        df = o.parse(js, datetime.now(timezone.utc)); t2 = time.time()
        print(f"{s}: fetch {t1 - t:.1f}s, parse {t2 - t1:.1f}s, options {len(js.get('data', {}).get('options', []))}, kept {len(df)}", flush=True)
    except Exception as e:
        print(f"{s}: FAILED after {time.time() - t:.1f}s {e!r}", flush=True)
