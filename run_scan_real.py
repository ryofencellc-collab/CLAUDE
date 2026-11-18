"""Blind-test follow-up (PROTOCOL_BLIND.md, 'Real-data scan'): run detector 2, the segment scanner that caught midday
and weekday patterns the grid can't express, on the real S&P and Nasdaq 1-minute data. Split 2012-2020 / 2021+."""
import pandas as pd, run_blind as RB
from edge import nygrid as G
from edge.intraday import load_nq

RB.SRC = ["SP", "NQ"]; RB.SPLIT = pd.Timestamp("2021-01-01")
_cache = {}
RB.load = lambda s: _cache.setdefault(s, G.day_matrix(load_nq(pair={"SP": "SPXUSD", "NQ": "NSXUSD"}[s])))
txt = RB.scan().replace("both years", "both periods (2012–2020 and 2021+)").replace("_2024", "_dev").replace("_2025", "_ho")
txt = txt.replace("## Detector 2: generic segment scanner", "# Segment scanner on real S&P and Nasdaq data")
txt += "\nColumns: *_dev = 2012–2020 (S&P from its first file), *_ho = 2021 → now. mean_bp = basis points per day before costs; a micro round trip costs about 1–2 bp.\n"
open("reports/SCAN_REAL.md", "w").write(txt); print(txt)
