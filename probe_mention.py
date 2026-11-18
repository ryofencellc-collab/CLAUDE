"""Probe for backlog #62: Kalshi mention markets + transcript sources. Writes probe/mention/."""
import json, os, re
import pandas as pd, requests
from edge import round27 as r27

OUT = "probe/mention"; os.makedirs(OUT, exist_ok=True)
ser = r27.series_list()
rows = [dict(ticker=s["ticker"], title=s.get("title"), category=s.get("category"), freq=s.get("frequency"))
        for s in ser if re.search(r"mention|say|said|word|speech|press conference|tweet", f"{s.get('title','')} {s.get('ticker','')}", re.I)]
S = pd.DataFrame(rows)
a, b = pd.Timestamp("2025-06-01", tz="UTC"), pd.Timestamp("2026-11-18", tz="UTC")
cnt, samples = [], {}
for t in S.ticker:
    ms = r27.settled_markets(t, a, b, max_pages=3)
    vol = sum(float(m.get("volume_fp") or 0) for m in ms)
    cnt.append(dict(ticker=t, settled=len(ms), events=len({m.get("event_ticker") for m in ms}), volume=vol))
    if ms and len(samples) < 40 and vol > 0:
        m = ms[-1]; samples[t] = {k: str(m.get(k))[:400] for k in ("ticker", "title", "yes_sub_title", "rules_primary", "rules_secondary", "close_time", "result", "volume_fp")}
S = S.merge(pd.DataFrame(cnt), on="ticker").sort_values("volume", ascending=False)
S.to_csv(f"{OUT}/series.csv", index=False); json.dump(samples, open(f"{OUT}/samples.json", "w"), indent=1)
src = {"fed_presconf_pdf": "https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20250917.pdf",
       "fed_calendar": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
       "whitehouse_remarks": "https://www.whitehouse.gov/remarks/", "rev_transcripts": "https://www.rev.com/blog/transcripts",
       "presidency_ucsb": "https://www.presidency.ucsb.edu/documents/app-categories/spoken-addresses-and-remarks/presidential/news-conferences"}
res = {}
for k, u in src.items():
    try:
        r = requests.get(u, timeout=30, headers={"User-Agent": "Mozilla/5.0 (research probe)"}); res[k] = dict(status=r.status_code, bytes=len(r.content), type=r.headers.get("content-type"))
    except Exception as e:
        res[k] = dict(error=repr(e)[:150])
json.dump(res, open(f"{OUT}/sources.json", "w"), indent=1)
print(S.head(50).to_string()); print(res)
