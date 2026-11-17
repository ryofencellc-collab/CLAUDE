"""One-off: hunt for free historical intraday option data (optionsDX tiers, FlashAlpha, Kaggle, HF)."""
import json, re, requests
H = {"User-Agent": "Mozilla/5.0 (research)"}
out = []
def get(u, **kw):
    try:
        r = requests.get(u, headers=H, timeout=40, **kw); return r
    except Exception as e:
        out.append(f"== {u}\nERR {e!r}"); return None
def text(html):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S); return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))
# optionsDX: WooCommerce store API with variation prices
r = get("https://www.optionsdx.com/wp-json/wc/store/v1/products", params={"per_page": 50})
if r is not None:
    out.append(f"== optionsdx store {r.status_code}")
    try:
        for p in r.json():
            out.append(f"{p['id']} {p['name']} price {p.get('prices',{}).get('price_range') or p.get('prices',{}).get('price')} variations {len(p.get('variations',[]))}")
            for v in p.get("variations", [])[:80]:
                out.append("   var " + json.dumps(v.get("attributes")))
    except Exception as e:
        out.append(f"parse {e!r} {r.text[:500]}")
for pid_page in ("https://www.optionsdx.com/faq/", "https://www.optionsdx.com/product/spy-option-chains/"):
    r = get(pid_page)
    if r is not None:
        t = text(r.text); out.append(f"== {pid_page} {r.status_code}")
        for kw in ("free", "Free", "$", "minute", "Minutely", "download", "account", "register"):
            for m in list(re.finditer(re.escape(kw), t))[:3]:
                out.append(f"   [{kw}] ...{t[max(0,m.start()-150):m.start()+200]}...")
# FlashAlpha
for u in ("https://flashalpha.com/pricing", "https://flashalpha.com/articles/historical-0dte-data-api-pin-risk-gamma-decay-replay"):
    r = get(u)
    if r is not None:
        t = text(r.text); out.append(f"== {u} {r.status_code}")
        for kw in ("free", "Free", "/mo", "historical", "minute", "SPY", "per month", "API key"):
            for m in list(re.finditer(re.escape(kw), t))[:2]:
                out.append(f"   [{kw}] ...{t[max(0,m.start()-150):m.start()+200]}...")
# Kaggle + HF searches
for q in ("0dte", "spx options", "spy options intraday", "options minute", "spxw", "option chain intraday", "spy option chain"):
    r = get("https://www.kaggle.com/api/v1/datasets/list", params={"search": q})
    if r is not None and r.ok:
        out.append(f"== kaggle '{q}'")
        for x in r.json()[:12]:
            out.append(f"   {x.get('ref')} | {x.get('lastUpdated','')[:10]} | {x.get('totalBytesNullable') or x.get('totalBytes')} | {x.get('titleNullable') or x.get('title')} | {(x.get('subtitleNullable') or '')[:120]}")
    r = get("https://huggingface.co/api/datasets", params={"search": q, "limit": 20})
    if r is not None and r.ok:
        out.append(f"== hf '{q}'")
        for x in r.json()[:20]:
            out.append(f"   {x.get('id')} | {x.get('lastModified','')[:10]} | gated={x.get('gated')} | {(x.get('description') or '')[:140].strip()}")
open("probe/optdata/report.txt", "w").write("\n".join(out)); print("\n".join(out)[:20000])
