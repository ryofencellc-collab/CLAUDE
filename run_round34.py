"""Round 34 (PROTOCOL_ROUND34.md): whale autopsy on Polymarket's public data."""
import json
import math
import re
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import requests

D = "https://data-api.polymarket.com/v2"
OUT = Path("reports/ROUND34.md")
RAW = Path("data/r34")
S = requests.Session()
S.headers["User-Agent"] = "research"


def get(path, params, tries=4):
    for i in range(tries):
        try:
            r = S.get(f"{D}/{path}", params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 ** i)
                continue
            return None
        except (requests.RequestException, ValueError):
            time.sleep(2 ** i)
    return None


def paged(path, params, max_rows):
    rows, cursor = [], None
    while len(rows) < max_rows:
        p = dict(params, **({"cursor": cursor} if cursor else {}))
        j = get(path, p)
        if not j:
            break
        rows += j.get("data", [])
        cursor = (j.get("pagination") or {}).get("next_cursor")
        if not cursor or not (j.get("pagination") or {}).get("has_more"):
            break
        time.sleep(0.15)
    return rows[:max_rows]


def boards():
    out = []
    for period in ("month", "all"):
        for cat in ("overall", "crypto", "sports", "politics", "weather", "economics", "culture", "finance"):
            rows = paged("leaderboard", {"timePeriod": period.upper(), "orderBy": "PNL", "category": cat, "limit": 50}, 100)
            for r in rows:
                out.append({"board": f"{cat}/{period}", **r})
            print(f"board {cat}/{period}: {len(rows)}", flush=True)
    return pd.DataFrame(out)


CATS = [("crypto up/down", r"up or down|updown"), ("crypto other", r"bitcoin|btc|ethereum|eth\b|solana|xrp|crypto"),
        ("weather", r"temperature|°f|°c|rain|snow|hurricane|weather"),
        ("politics", r"election|trump|president|senate|house|governor|mayor|vote|poll|congress|minister|party"),
        ("sports", r" vs\.? | win on |o/u|spread|nfl|nba|mlb|nhl|ufc|premier|league|cup|match|game|tennis|atp|wta|f1|grand prix|open\b"),
        ]


def category(title, slug):
    s = f"{title} {slug}".lower()
    for name, pat in CATS:
        if re.search(pat, s):
            return name
    return "other"


def updown_end(slug):
    m = re.search(r"(\d{10})$", slug or "")
    if not m:
        return None
    start = int(m.group(1))
    span = 900 if "15m" in slug else 300 if "5m" in slug else 3600 if "1h" in slug or "hourly" in slug else 900
    return start + span


def profile(w, trades, acts):
    t = pd.DataFrame(trades)
    if t.empty:
        return {}
    t["usd"] = t["size"].astype(float) * t["price"].astype(float)
    t["cat"] = [category(a, b) for a, b in zip(t["title"], t.get("event_slug", t["slug"]))]
    buys = t[t["side"] == "BUY"]
    days = max((t["timestamp"].max() - t["timestamp"].min()) / 86400, 1 / 24)
    both = t.groupby("condition_id")["outcome_index"].nunique()
    hours = pd.to_datetime(t["timestamp"], unit="s").dt.hour.value_counts(normalize=True)
    ent = float(-(hours * np.log(hours)).sum() / math.log(24))
    ud = t[t["cat"] == "crypto up/down"].copy()
    if len(ud):
        ud["end"] = ud["slug"].map(updown_end)
        ud["secs_left"] = ud["end"] - ud["timestamp"]
    cm = t["cat"].value_counts(normalize=True)
    rebates = sum(1 for a in acts if "REBATE" in str(a.get("type", "")).upper())
    return {"trades": len(t), "markets": t["condition_id"].nunique(), "trades_per_day": len(t) / days,
            "median_usd": float(t["usd"].median()), "total_usd": float(t["usd"].sum()),
            "buy_share": float((t["side"] == "BUY").mean()),
            "buys_ge90": float((buys["price"] >= 0.90).mean()) if len(buys) else 0.0,
            "buys_le10": float((buys["price"] <= 0.10).mean()) if len(buys) else 0.0,
            "both_sides": float((both > 1).mean()), "hour_entropy": ent, "rebates": rebates,
            "top_cat": cm.index[0], "top_cat_share": float(cm.iloc[0]),
            "cat_mix": ", ".join(f"{k} {v:.0%}" for k, v in cm.head(3).items()),
            "updown_median_secs_left": float(ud["secs_left"].median()) if len(ud) and ud["secs_left"].notna().any() else np.nan,
            "updown_buy_price_median": float(ud[ud["side"] == "BUY"]["price"].median()) if len(ud) else np.nan}


def archetype(p):
    if not p:
        return "no data"
    if p["markets"] >= 200 and (p["both_sides"] >= 0.40 or p["rebates"] > 0):
        return "market maker"
    if p["markets"] < 30:
        return "sniper"
    if p["buys_ge90"] >= 0.50:
        return "late-favourite closer"
    if p["buys_le10"] >= 0.40:
        return "long-shot buyer"
    if p["top_cat_share"] >= 0.70:
        return f"specialist ({p['top_cat']})"
    return "mixed"


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    b = boards()
    b.to_csv(RAW / "boards.csv", index=False)
    wallets = b.sort_values("pnl", ascending=False).drop_duplicates("user_id")
    wallets = wallets.head(250)
    rows = []
    for i, w in enumerate(wallets.itertuples(index=False)):
        tr = paged("trades", {"user": w.user_id, "limit": 500}, 3000)
        ac = paged("activity", {"user": w.user_id, "limit": 500}, 1000)
        p = profile(w.user_id, tr, ac)
        rows.append({"wallet": w.user_id, "name": w.user_name, "board": w.board, "pnl": w.pnl, "volume": w.volume,
                     "archetype": archetype(p), **p})
        json.dump({"trades": tr[:3000], "activity": ac}, open(RAW / f"{w.user_id}.json", "w"))
        if i % 10 == 0:
            print(f"{i}/{len(wallets)} {w.user_name}: {archetype(p)}", flush=True)
    d = pd.DataFrame(rows)
    d.to_csv(RAW / "profiles.csv", index=False)
    d.to_csv("reports/ROUND34.csv", index=False)
    arch = d.groupby("archetype").agg(wallets=("wallet", "size"), total_pnl=("pnl", "sum"), median_pnl=("pnl", "median"),
                                      median_markets=("markets", "median"), median_trades_per_day=("trades_per_day", "median"),
                                      median_trade_usd=("median_usd", "median")).sort_values("total_pnl", ascending=False)
    top = d.sort_values("pnl", ascending=False).head(25)
    cols = ["name", "board", "pnl", "volume", "archetype", "markets", "trades_per_day", "median_usd", "buys_ge90", "buys_le10",
            "both_sides", "hour_entropy", "rebates", "cat_mix", "updown_median_secs_left", "updown_buy_price_median"]
    bycat = d.groupby("top_cat").agg(wallets=("wallet", "size"), total_pnl=("pnl", "sum")).sort_values("total_pnl", ascending=False)
    lines = ["# Round 34: whale autopsy — what Polymarket's top wallets do", "",
             "Rules: [PROTOCOL_ROUND34.md](../PROTOCOL_ROUND34.md). Leaderboard PnL is Polymarket's; behaviour from each "
             "wallet's last ≤ 3,000 trades.", "", f"Wallets profiled: {len(d)} (top by PnL across {b['board'].nunique()} boards).", "",
             "## Archetypes", "", arch.round(2).to_markdown(), "", "## Main category of the top wallets", "", bycat.round(0).to_markdown(), "",
             "## Top 25 wallets", "", top[cols].round(3).to_markdown(index=False), "",
             "Columns: buys_ge90 / buys_le10 = share of buys at ≥ 90c / ≤ 10c; both_sides = share of markets where the wallet "
             "bought both outcomes; hour_entropy 1.0 = trades evenly round the clock (a bot), low = a human's hours; "
             "updown_* = 5/15-minute crypto markets only."]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
