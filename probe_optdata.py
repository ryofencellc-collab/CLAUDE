"""One-off: optionsDX SPX/SPY variation prices (which year/frequency combos are free)."""
import json, requests
H = {"User-Agent": "Mozilla/5.0 (research)"}
B = "https://www.optionsdx.com/wp-json/wc/store/v1/products"
out = []
for pid in (74, 341, 828):
    p = requests.get(f"{B}/{pid}", headers=H, timeout=40).json()
    out.append(f"== {p.get('name')} range {p.get('prices',{}).get('price_range')}")
    rows = []
    for v in p.get("variations", []):
        vv = requests.get(f"{B}/{v['id']}", headers=H, timeout=40).json()
        pr = vv.get("prices", {})
        price = int(pr.get("price", 0)) / (10 ** pr.get("currency_minor_unit", 2))
        attrs = {a["name"]: a["value"] for a in v.get("attributes", [])}
        rows.append((attrs.get("Year") or attrs.get("Period"), attrs.get("Quote Frequency"), price))
    for r in sorted(rows):
        out.append(f"   {r[0]} | {r[1]} | ${r[2]:,.2f}")
open("probe/optdata/prices.txt", "w").write("\n".join(out)); print("\n".join(out))
