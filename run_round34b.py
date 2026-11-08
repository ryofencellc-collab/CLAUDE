"""Round 34b: take the top bot wallets apart trade by trade (price, side, timing, result) to recover their rule."""
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

import run_round34 as r34

G = "https://gamma-api.polymarket.com"
OUT = Path("reports/ROUND34B.md")
_m: dict = {}


def market(slug):
    if slug in _m:
        return _m[slug]
    out = None
    for i in range(3):
        try:
            r = r34.S.get(f"{G}/markets", params={"slug": slug}, timeout=30)
            if r.status_code == 200 and r.json():
                out = r.json()[0]
                break
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(1 + i)
    _m[slug] = out
    time.sleep(0.12)
    return out


def template(title):
    t = re.sub(r"\d+(\.\d+)?", "#", title or "")
    t = re.sub(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b", "MON", t)
    return " ".join(t.split()[:9])


def analyse(name, wallet):
    tr = pd.DataFrame(r34.paged("trades", {"user": wallet, "limit": 500}, 5000))
    if tr.empty:
        return None, []
    tr["usd"] = tr["size"] * tr["price"]
    slugs = tr.drop_duplicates("slug").sort_values("timestamp", ascending=False)["slug"].head(500)
    info = {}
    for s in slugs:
        m = market(s)
        if not m:
            continue
        try:
            prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        except (TypeError, ValueError):
            prices = []
        info[s] = {"end": pd.to_datetime(m.get("endDate"), utc=True, errors="coerce"),
                   "closed": pd.to_datetime(m.get("closedTime"), utc=True, errors="coerce"),
                   "resolved": bool(prices) and max(prices) >= 0.99 and m.get("closed"), "prices": prices,
                   "category": m.get("category")}
    tr = tr[tr["slug"].isin(info)].copy()
    tr["t"] = pd.to_datetime(tr["timestamp"], unit="s", utc=True)
    tr["end"] = tr["slug"].map(lambda s: info[s]["closed"] if pd.notna(info[s]["closed"]) else info[s]["end"])
    tr["hours_left"] = (tr["end"] - tr["t"]).dt.total_seconds() / 3600
    tr["resolved"] = tr["slug"].map(lambda s: info[s]["resolved"])
    tr["won"] = [float(info[s]["prices"][i] >= 0.99) if info[s]["resolved"] and i < len(info[s]["prices"]) else np.nan
                 for s, i in zip(tr["slug"], tr["outcome_index"])]
    tr["pnl"] = np.where(tr["side"] == "BUY", tr["size"] * (tr["won"] - tr["price"]), tr["size"] * (tr["price"] - tr["won"]))
    tr["cat"] = [r34.category(a, b) for a, b in zip(tr["title"], tr["slug"])]
    tr["template"] = tr["title"].map(template)
    b = tr[(tr["side"] == "BUY") & tr["resolved"]]
    bins = [0, 0.10, 0.50, 0.80, 0.90, 0.95, 0.98, 0.99, 0.995, 1.0001]
    labels = ["<10c", "10-50c", "50-80c", "80-90c", "90-95c", "95-98c", "98-99c", "99-99.5c", "99.5c+"]
    b = b.assign(band=pd.cut(b["price"], bins, labels=labels, right=False))
    by_band = b.groupby("band", observed=True).agg(trades=("price", "size"), usd=("usd", "sum"), avg_price=("price", "mean"),
                                                  win_rate=("won", "mean"), pnl=("pnl", "sum"),
                                                  median_hours_left=("hours_left", "median")).round(4)
    lost = b[b["won"] == 0].sort_values("usd", ascending=False).head(5)[["title", "outcome", "price", "usd", "hours_left"]]
    tmpl = tr.groupby("template").agg(trades=("price", "size"), usd=("usd", "sum"), pnl=("pnl", "sum")).sort_values("trades", ascending=False).head(8)
    summ = {"name": name, "trades": len(tr), "resolved buys": len(b), "buy win rate": round(b["won"].mean(), 4) if len(b) else np.nan,
            "pnl on these trades": round(b["pnl"].sum() + tr[(tr["side"] == "SELL") & tr["resolved"]]["pnl"].sum(), 2),
            "yes share of buys": round((b["outcome"].str.lower() == "yes").mean(), 2) if len(b) else np.nan,
            "median hours left": round(b["hours_left"].median(), 2) if len(b) else np.nan,
            "sell share": round((tr["side"] == "SELL").mean(), 2)}
    sec = [f"## {name}", "", f"`{wallet}`", "", pd.DataFrame([summ]).to_markdown(index=False), "", "Buys by price paid:", "",
           by_band.to_markdown(), "", "What it trades most:", "", tmpl.round(2).to_markdown(), "", "Its biggest losing buys:", "",
           lost.round(3).to_markdown(index=False) if len(lost) else "none", ""]
    return summ, sec


def main():
    w = pd.read_csv("control/r34b_wallets.csv")
    lines = ["# Round 34b: the top bot wallets, trade by trade", "",
             "Each wallet's last ≤ 5,000 trades; markets looked up on Polymarket's Gamma API for end time and result. "
             "PnL here = per-trade P&L on resolved markets (before fees), to recover the rule, not to rank.", ""]
    summs, secs = [], []
    for x in w.itertuples(index=False):
        s, sec = analyse(x.name[:30], x.wallet)
        print(x.name[:30], s, flush=True)
        if s:
            summs.append(s)
            secs += sec
    lines += ["## Summary", "", pd.DataFrame(summs).to_markdown(index=False), ""] + secs
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
