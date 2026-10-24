"""Download HistData NSXUSD 1-minute bars (yearly files, monthly for the current year)."""
import zipfile
from pathlib import Path

import pandas as pd
from histdata import download_hist_data as dl
from histdata.api import Platform as P, TimeFrame as TF

OUT = Path(__file__).resolve().parent / "data" / "histdata"
OUT.mkdir(parents=True, exist_ok=True)
now = pd.Timestamp.utcnow()
jobs = [(str(y), None) for y in range(2012, now.year)] + \
       [(str(now.year), str(m)) for m in range(1, now.month)]
for year, month in jobs:
    tag = year + (f"{int(month):02d}" if month else "")
    if (OUT / f"DAT_ASCII_NSXUSD_M1_{tag}.csv").exists():
        continue
    try:
        z = dl(year=year, month=month, pair="nsxusd", platform=P.GENERIC_ASCII,
               time_frame=TF.ONE_MINUTE, output_directory=str(OUT), verbose=False)
        with zipfile.ZipFile(z) as f:
            f.extractall(OUT)
        Path(z).unlink()
        print("ok", tag, flush=True)
    except Exception as e:  # current month or a missing file
        print("skip", tag, repr(e), flush=True)
