"""Round 9b runner (PROTOCOL_ROUND9B.md): data-chosen trade gates on US stock ETFs.

    python run_round9b.py            # full: 13 ETFs
    R9_SMALL=1 python run_round9b.py # smoke: SPY and QQQ only
"""
import os
import time

import pandas as pd

from edge import gates
from run_round9 import report

SMALL = os.environ.get("R9_SMALL") == "1"
ETFS = ["SPY", "QQQ"] if SMALL else ["SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE", "XLV", "XLY", "XLP",
                                     "XLI", "XLB", "XLU"]
MACRO = ["^VIX", "^VIX3M", "^IRX", "HYG", "IEF", "TLT", "SPY"]


def download(tickers):
    import yfinance as yf
    for attempt, wait in enumerate((0, 60, 300)):  # polite: one batch, back off if Yahoo rate-limits
        time.sleep(wait)
        raw = yf.download(sorted(set(tickers)), start="2007-06-01", auto_adjust=True, progress=False, threads=False)
        close = raw["Close"] if raw is not None and not raw.empty else pd.DataFrame()
        missing = [t for t in set(tickers) if t not in close or close[t].notna().sum() < 1000]
        print(f"  attempt {attempt + 1}: {len(set(tickers)) - len(missing)} of {len(set(tickers))} tickers", flush=True)
        if not missing:
            close.index = pd.DatetimeIndex(close.index).tz_localize(None)
            return close
    raise RuntimeError(f"Yahoo returned no data for {missing}")


def main():
    close = download(ETFS + MACRO)
    px = close[ETFS].dropna(how="all")
    macro = close[MACRO]
    print(f"ETFs: {px.shape[1]}, {px.index[0].date()} to {px.index[-1].date()}", flush=True)
    p = {"spot_close": px, "spot_qv": pd.DataFrame(1.0, index=px.index, columns=px.columns)}
    lib = gates.library(gates.stock_base_gates(px, macro))
    oos, turn, log = gates.walk_forward(p, mkt=gates.STOCKS, lib=lib)
    v = gates.verdict(oos, turn, macro["SPY"].reindex(px.index), 265, 252)
    report(oos, turn, log, v, macro["SPY"].reindex(px.index), "SPY", 252, "PROTOCOL_ROUND9B.md", 265,
           "ROUND9B_SMOKE.md" if SMALL else "ROUND9B.md",
           "b SMOKE TEST (SPY+QQQ, pipeline check, not a result)" if SMALL else "b (US stock ETFs)")


if __name__ == "__main__":
    main()
