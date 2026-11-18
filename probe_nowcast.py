"""Probe for Round 57 (AUTONOMOUS.md): which Kalshi series settle on public statistics, how many settled markets, and do the data
sources answer from GitHub Actions? Writes probe/nowcast/."""
import json, os, re
import pandas as pd, requests
from edge import round27 as r27

OUT = "probe/nowcast"; os.makedirs(OUT, exist_ok=True)
KEYS = r"tsa|gas|cpi|inflation|jobless|claims|payroll|unemploy|gdp|mortgage|pce|retail sales|housing|spotify|billboard|box office|rotten|chart|song|album|egg|fed funds|treasury|10-year|pmi|ism|jolts|consumer sentiment"
ser = r27.series_list()
rows = []
for s in ser:
    txt = f"{s.get('title','')} {s.get('ticker','')} {s.get('category','')}"
    if re.search(KEYS, txt, re.I):
        rows.append(dict(ticker=s["ticker"], title=s.get("title"), category=s.get("category"), freq=s.get("frequency"), volume=s.get("volume")))
S = pd.DataFrame(rows).sort_values("volume", ascending=False) if rows else pd.DataFrame()
a, b = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-11-18", tz="UTC")
counts = []
for t in S.ticker.head(60) if len(S) else []:
    ms = r27.settled_markets(t, a, b, max_pages=5)
    counts.append(dict(ticker=t, settled_markets=len(ms), events=len({m.get("event_ticker") for m in ms}),
                       example=(ms[0].get("title") if ms else ""), rules=(ms[0].get("rules_primary", "")[:200] if ms else "")))
C = pd.DataFrame(counts)
if len(S): S = S.merge(C, on="ticker", how="left")
S.to_csv(f"{OUT}/series.csv", index=False)
src = {"tsa": "https://www.tsa.gov/travel/passenger-volumes", "fred_icsa": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=ICSA",
       "fred_gas": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GASREGW", "eia_gas": "https://www.eia.gov/dnav/pet/hist_xls/EMM_EPMR_PTE_NUS_DPGw.xls",
       "gdpnow": "https://www.atlantafed.org/-/media/documents/cqer/researchcq/gdpnow/GDPTrackingModelDataAndForecasts.xlsx",
       "cleveland_nowcast": "https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting",
       "kworb_spotify": "https://kworb.net/spotify/country/us_daily.html", "aaa_gas": "https://gasprices.aaa.com/",
       "freddie_pmms": "https://www.freddiemac.com/pmms/docs/PMMS_history.csv", "boxofficemojo": "https://www.boxofficemojo.com/weekend/"}
res = {}
for k, u in src.items():
    try:
        r = requests.get(u, timeout=30, headers={"User-Agent": "Mozilla/5.0 (research probe)"})
        res[k] = dict(status=r.status_code, bytes=len(r.content), head=r.text[:160].replace("\n", " ") if "text" in r.headers.get("content-type", "") or "csv" in u else r.headers.get("content-type"))
    except Exception as e:
        res[k] = dict(error=repr(e)[:200])
json.dump(res, open(f"{OUT}/sources.json", "w"), indent=1)
print(S.head(60).to_string()); print(json.dumps(res, indent=1))
