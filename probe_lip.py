"""One-off: Kalshi liquidity-incentive rules text + order books of a sample of program markets."""
import json, os, random, re, time, requests
os.makedirs("probe/lip", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0 (research probe)"}
K = "https://api.elections.kalshi.com/trade-api/v2"
out = {}
for name, u in [("help", "https://help.kalshi.com/en/articles/13823851-liquidity-incentive-program"),
                ("help_search", "https://help.kalshi.com/en/?q=liquidity+incentive"),
                ("fees", "https://kalshi.com/fee-schedule"),
                ("docs_inc", "https://docs.kalshi.com/api-reference/incentive-programs/get-incentives")]:
    try:
        r = requests.get(u, headers=H, timeout=30)
        t = re.sub(r"<script.*?</script>|<style.*?</style>", "", r.text, flags=re.S)
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))
        out[name] = [r.status_code, t[:20000]]
    except Exception as e:
        out[name] = repr(e)
progs = json.load(open("probe/rewards/kalshi_programs.json"))
random.seed(44); sample = random.sample(progs, min(150, len(progs)))
books = []
for p in sample:
    t = p["market_ticker"]
    r = requests.get(f"{K}/markets/{t}/orderbook", headers=H, timeout=20)
    m = requests.get(f"{K}/markets/{t}", headers=H, timeout=20)
    books.append({"program": p, "book": r.json() if r.status_code == 200 else None,
                  "market": m.json().get("market") if m.status_code == 200 else None})
    time.sleep(0.15)
json.dump(books, open("probe/lip/books.json", "w"))
json.dump(out, open("probe/lip/report.json", "w"), indent=1)
print({k: (v[0], v[1][:300]) if isinstance(v, list) else v for k, v in out.items()})
