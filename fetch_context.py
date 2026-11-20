"""Round 62 context data: 1-minute Yahoo bars for market-wide variables on each recorded 0DTE day.
Saved to data/ctx/<day>.csv.gz (force-added to git so nightly CI keeps history beyond Yahoo's 30-day 1m window)."""
import glob, os, sys, time
import pandas as pd, yfinance as yf

TICKERS = ["SPY", "^VIX", "QQQ", "IWM", "NVDA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "TSLA", "^TNX", "DX-Y.NYB", "BTC-USD", "TLT", "HYG"]
OUT = "data/ctx"; os.makedirs(OUT, exist_ok=True)


def main():
    days = sorted(os.path.basename(p) for p in glob.glob("data/odte/2*"))
    todo = [d for d in days if not os.path.exists(f"{OUT}/{d}.csv.gz") and (pd.Timestamp.now() - pd.Timestamp(d)).days <= 28]
    for d in todo:
        a, b = pd.Timestamp(d), pd.Timestamp(d) + pd.Timedelta(days=1)
        frames = []
        for tk in TICKERS:
            for k in range(3):
                try:
                    x = yf.download(tk, start=a.strftime("%Y-%m-%d"), end=b.strftime("%Y-%m-%d"), interval="1m", progress=False, auto_adjust=False)
                    break
                except Exception as e:
                    print(tk, d, repr(e)); time.sleep(3); x = pd.DataFrame()
            if x is None or x.empty: print("empty", tk, d); continue
            x.columns = [c[0] if isinstance(c, tuple) else c for c in x.columns]
            x = x[["Close", "Volume"]].rename(columns={"Close": f"{tk}_close", "Volume": f"{tk}_vol"})
            x.index = pd.to_datetime(x.index, utc=True).tz_convert("America/New_York")
            frames.append(x)
        if frames:
            C = pd.concat(frames, axis=1).sort_index(); C.to_csv(f"{OUT}/{d}.csv.gz"); print("saved", d, C.shape, flush=True)


if __name__ == "__main__":
    main()
