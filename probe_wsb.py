"""One-off: summarize ./body (HF tree listing or text)."""
import json
raw = open("body", errors="replace").read()
try:
    d = json.loads(raw)
except Exception:
    print(raw[:1500]); raise SystemExit
if isinstance(d, list):
    for x in d[:60]:
        print(x.get("path"), x.get("type"), x.get("size"))
else:
    print(json.dumps(d)[:1500])
