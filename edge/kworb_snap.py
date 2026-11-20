"""Backlog 58b collector: hourly snapshots of kworb's Spotify daily charts (top 20 with stream counts) and the Kalshi Spotify #1 markets' quotes.
No free history exists, so the 58b test (stream gap -> next #1 vs price) needs this forward record first. Output: paper/r58b/<UTC date>_{kworb,kalshi}.csv."""
import gzip, io, os, time
import pandas as pd, requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "paper", "r58b"); os.makedirs(OUT, exist_ok=True)
PAGES = {"us": "https://kworb.net/spotify/country/us_daily.html", "global": "https://kworb.net/spotify/country/global_daily.html"}
SERIES = ["KXSPOTIFYD", "KXSPOTIFY2D", "KXSPOTIFYGLOBALD"]
STAMP = os.path.join(OUT, ".last")


def _append(path, df):
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)


def snap(get, min_gap_s=3300):
    """get(path, params) -> Kalshi JSON (mention_live.get). Runs at most once per ~hour."""
    try:
        last = pd.Timestamp(open(STAMP).read().strip())
        if (pd.Timestamp.now(tz="UTC") - last).total_seconds() < min_gap_s: return []
    except Exception:
        pass
    now = pd.Timestamp.now(tz="UTC"); day = now.strftime("%Y-%m-%d"); wrote = []
    for chart, url in PAGES.items():
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "research-probe"}); r.raise_for_status()
            T = pd.read_html(io.StringIO(r.text))[0].head(20)
            T.columns = [str(c) for c in T.columns]
            T.insert(0, "chart", chart); T.insert(0, "time", now.isoformat())
            p = os.path.join(OUT, f"{day}_kworb.csv"); _append(p, T); wrote.append(p)
        except Exception as e:
            print("kworb", chart, "failed:", repr(e), flush=True)
            try:
                p = os.path.join(OUT, f"{day}_{chart}_{now:%H%M}.html.gz"); gzip.open(p, "wt").write(r.text); wrote.append(p)
            except Exception:
                pass
    rows = []
    for s in SERIES:
        j = get("markets", {"series_ticker": s, "status": "open", "limit": 1000}) or {}
        for m in j.get("markets", []):
            rows.append(dict(time=now.isoformat(), series=s, ticker=m["ticker"], event=m.get("event_ticker"), title=m.get("yes_sub_title"),
                             yes_bid=m.get("yes_bid_dollars"), yes_ask=m.get("yes_ask_dollars"), volume=m.get("volume_fp"), close=m.get("close_time")))
    if rows:
        p = os.path.join(OUT, f"{day}_kalshi.csv"); _append(p, pd.DataFrame(rows)); wrote.append(p)
    open(STAMP, "w").write(now.isoformat()); print("r58b snapshot:", len(rows), "kalshi quotes;", wrote, flush=True)
    return wrote
