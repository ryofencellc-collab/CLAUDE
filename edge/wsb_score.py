"""Round 50 scorer (PROTOCOL_ROUND50.md): score the pre-registered Reddit crowd-emotion strategies on collected snapshots."""
from __future__ import annotations
import glob, math, os
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "wsb")
REPORT = os.path.join(ROOT, "reports", "ROUND50.md")
COST = 0.001
CUT_UTC_HOUR = 20          # 15:00 ET in winter (EST); the protocol's "at or before 15:00 ET"


def load_snaps() -> pd.DataFrame:
    fs = sorted(glob.glob(os.path.join(DATA, "*.csv.gz")))
    if not fs:
        return pd.DataFrame()
    d = pd.concat((pd.read_csv(f) for f in fs), ignore_index=True)
    d = d[d["filter"] == "all-stocks"].copy()
    d["ts"] = pd.to_datetime(d["ts"], utc=True)
    for c in ("mentions", "upvotes", "mentions_24h_ago"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d


def daily_signals(d: pd.DataFrame, days: pd.DatetimeIndex) -> dict:
    """{day: {"A1": [...], "A4": [...], "A5": [...]}} from the last snapshot at/before the cut on that day."""
    out = {}
    for day in days:
        cut = pd.Timestamp(day.date(), tz="UTC") + pd.Timedelta(hours=CUT_UTC_HOUR)
        s = d[(d.ts <= cut) & (d.ts > cut - pd.Timedelta(hours=24))]
        if s.empty:
            continue
        s = s[s.ts == s.ts.max()]
        s = s[s.mentions >= 50].copy()
        if len(s) < 10:
            continue
        s["surge"] = s.mentions / s.mentions_24h_ago.fillna(0).clip(lower=10)
        s["approval"] = s.upvotes / s.mentions
        out[day] = {"A1": s.nlargest(10, "surge").ticker.tolist(), "A4": s.nlargest(10, "mentions").ticker.tolist(),
                    "A5": s.nlargest(10, "approval").ticker.tolist()}
    return out


def basket_returns(sig: dict, px: pd.DataFrame, key: str, hold: int) -> pd.Series:
    """Daily return of overlapping equal-weight sleeves: each day's basket is bought at that close and held `hold` days."""
    r = px.pct_change(fill_method=None)
    days = sorted(sig); idx = px.index
    out = pd.Series(0.0, index=idx); n = pd.Series(0, index=idx)
    for day in days:
        names = [t for t in sig[day][key] if t in px.columns and np.isfinite(px.at[day, t] if day in px.index else np.nan) and px.at[day, t] >= 5]
        if not names or day not in idx:
            continue
        i = idx.get_loc(day)
        for j in range(i + 1, min(i + hold, len(idx) - 1) + 1):
            out.iloc[j] += r.iloc[j][names].mean() / hold
        if i + 1 < len(idx):
            out.iloc[i + 1] -= 2 * COST / hold
            n.iloc[i + 1] += 1
    if not days:
        return out.iloc[:0]
    end = idx[min(idx.searchsorted(max(days)) + hold, len(idx) - 1)]
    return out[(out.index > min(days)) & (out.index <= end)]


def stats(x: pd.Series, spy: pd.Series) -> dict:
    x = x.dropna()
    if len(x) < 2:
        return dict(days=len(x), total=np.nan, ann=np.nan, excess_t=np.nan, worst_drop=np.nan)
    ex = x - spy.reindex(x.index).fillna(0)
    eq = (1 + x).cumprod()
    return dict(days=len(x), total=eq.iloc[-1] - 1, ann=(eq.iloc[-1]) ** (252 / len(x)) - 1,
                excess_t=ex.mean() / ex.std() * math.sqrt(len(x)) if ex.std() > 0 else np.nan, worst_drop=(eq / eq.cummax() - 1).min())


def main(prices=None):
    d = load_snaps()
    lines = ["# Round 50: Reddit crowd-emotion strategies (forward, from ApeWisdom snapshots)", "",
             "Rules: [PROTOCOL_ROUND50.md](../PROTOCOL_ROUND50.md). Verdict after 40 trading days.", ""]
    if d.empty:
        open(REPORT, "w").write("\n".join(lines + ["No snapshots yet."]) + "\n"); return
    tickers = sorted(set(d.ticker.dropna().astype(str)))
    first, last = d.ts.min().normalize().tz_localize(None), pd.Timestamp.now().normalize()
    if prices is None:
        import yfinance as yf
        px = yf.download(tickers + ["SPY"], start=str((first - pd.Timedelta(days=5)).date()), auto_adjust=True, progress=False)["Close"]
        px.index = pd.to_datetime(px.index).tz_localize(None)
    else:
        px = prices
    days = px.index[(px.index >= first) & (px.index <= last)]
    sig = daily_signals(d, days)
    spy = px["SPY"].pct_change(fill_method=None)
    series = {"A1 hype momentum, 1 day": basket_returns(sig, px, "A1", 1), "A2 hype momentum, 5 days": basket_returns(sig, px, "A1", 5),
              "A4 most mentioned, 5 days": basket_returns(sig, px, "A4", 5), "A5 approval, 5 days": basket_returns(sig, px, "A5", 5)}
    series["A3 hype fade (short), 1 day"] = -series["A1 hype momentum, 1 day"] - 4 * COST * (series["A1 hype momentum, 1 day"] != 0)
    rows = []
    for k, x in series.items():
        s = stats(x, spy)
        rows.append({"strategy": k, "days": s["days"], "total": f"{s['total']:.1%}" if pd.notna(s["total"]) else "",
                     "annualized": f"{s['ann']:.0%}" if pd.notna(s["ann"]) else "", "excess t": round(s["excess_t"], 2) if pd.notna(s["excess_t"]) else "",
                     "worst drop": f"{s['worst_drop']:.1%}" if pd.notna(s["worst_drop"]) else ""})
    lines += [f"Signal days so far: {len(sig)}. SPY over the same days: {((1 + spy.reindex(series['A1 hype momentum, 1 day'].index).fillna(0)).prod() - 1):.1%}.", "",
              pd.DataFrame(rows).to_markdown(index=False)]
    if sig:
        lastday = max(sig); lines += ["", f"Latest baskets ({lastday.date()}): hype {', '.join(sig[lastday]['A1'])}; "
                                          f"most mentioned {', '.join(sig[lastday]['A4'])}"]
    open(REPORT, "w").write("\n".join(lines) + "\n"); print("\n".join(lines))


if __name__ == "__main__":
    main()
