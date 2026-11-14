"""One-off: summarize a JSON listing saved as ./body (ApeWisdom / HF / Kaggle)."""
import json
try:
    d = json.load(open("body"))
except Exception:
    print(open("body", errors="replace").read()[:800]); raise SystemExit
if isinstance(d, dict) and "results" in d:
    print("count", d.get("count"), "pages", d.get("pages")); print(json.dumps(d["results"][:5])[:1200])
elif isinstance(d, list):
    for x in d[:40]:
        print(x.get("id") or x.get("ref"), "|", (x.get("lastModified") or x.get("lastUpdated") or "")[:10], "|",
              x.get("downloads") or x.get("downloadCount"), "|",
              (x.get("description") or x.get("subtitleNullable") or x.get("titleNullable") or "")[:160].replace("\n", " "))
