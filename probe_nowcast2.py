"""Probe 2 for Round 57: market structure + history depth for candidate nowcast series. Writes probe/nowcast/detail.*"""
import json, os
import pandas as pd
from edge import round27 as r27

OUT = "probe/nowcast"; os.makedirs(OUT, exist_ok=True)
ser = [s["ticker"] for s in r27.series_list()]
gas = sorted(t for t in ser if t.startswith("KXAAAGASD"))
cands = ["KXAAAGASD", "KXAAAGASW", "KXAAAGASM", "KXTGAW", "FRM", "KX30YMORTW", "KXJOBLESSCLAIMS", "KXSPOTIFYD", "KXHOT100", "KXTRUFTSA",
         "KXTNOTED", "KXTNOTEW", "KXSPOTIFY2D", "KXSPOTIFYARTISTD", "KXUSHOMEINVENT", "KXNATGASD"] + gas[:6]
a, b = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-11-18", tz="UTC")
cut = r27.cutoff(); summary, samples = [], {}
for t in dict.fromkeys(cands):
    ms = r27.settled_markets(t, a, b, max_pages=10)
    if not ms:
        summary.append(dict(series=t, settled=0)); continue
    ms = sorted(ms, key=lambda m: m.get("close_time", ""))
    m = ms[-1]
    close = pd.to_datetime(m.get("close_time"), utc=True)
    tr = r27.trades(m["ticker"], close, cut, max_pages=2)
    vol = sum(float(x.get("count_fp") or x.get("count") or 0) for x in tr)
    summary.append(dict(series=t, settled=len(ms), events=len({x.get("event_ticker") for x in ms}), first=ms[0].get("close_time"), last=m.get("close_time"),
                        n_trades_last_mkt=len(tr), contracts_last_mkt=vol, has_exp_value=sum(1 for x in ms if x.get("expiration_value") not in (None, ""))))
    samples[t] = {k: m.get(k) for k in ("ticker", "event_ticker", "title", "subtitle", "yes_sub_title", "rules_primary", "rules_secondary", "open_time",
                                        "close_time", "expiration_value", "result", "strike_type", "floor_strike", "cap_strike", "volume", "volume_fp", "last_price_dollars")}
    samples[t]["first_trades"] = tr[:3]
S = pd.DataFrame(summary); S.to_csv(f"{OUT}/detail.csv", index=False)
json.dump(samples, open(f"{OUT}/detail_samples.json", "w"), indent=1, default=str)
print("gas series:", len(gas), gas[:60]); print(S.to_string())
