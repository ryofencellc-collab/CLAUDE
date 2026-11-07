"""Round 27 (PROTOCOL_ROUND27.md): scan every Kalshi series for the 99c maker edge, honestly counted."""
import numpy as np
import pandas as pd

from edge import round15 as r15
from edge import weather as wx

CAPTURE, CAP, LO, HI = 0.25, 1000.0, 0.01, 0.02


def series_list() -> list[dict]:
    r = wx._get(f"{wx.KALSHI}/series", {"include_volume": "true"})
    return (r.json().get("series") or []) if r is not None and r.status_code == 200 else []


def settled_markets(series: str, a: pd.Timestamp, b: pd.Timestamp, max_pages: int = 20) -> list[dict]:
    out, cursor = [], None
    for _ in range(max_pages):
        p = {"series_ticker": series, "min_close_ts": int(a.timestamp()), "max_close_ts": int(b.timestamp()), "limit": 1000}
        if cursor:
            p["cursor"] = cursor
        r = wx._get(f"{wx.KALSHI}/markets", p)
        if r is None or r.status_code != 200:
            break
        j = r.json()
        out += [m for m in j.get("markets", []) if m.get("result") in ("yes", "no")]
        cursor = j.get("cursor")
        if not cursor or not j.get("markets"):
            break
    return out


def cutoff() -> pd.Timestamp:
    r = wx._get(f"{wx.KALSHI}/historical/cutoff")
    try:
        return pd.Timestamp(r.json()["trades_created_ts"], unit="s", tz="UTC") if r is not None and r.status_code == 200 \
            else pd.Timestamp.now(tz="UTC")
    except (KeyError, ValueError, TypeError):
        return pd.Timestamp.now(tz="UTC")


def trades(ticker: str, close: pd.Timestamp, hist_cut: pd.Timestamp, max_pages: int = 30) -> list[dict]:
    """Every trade in the market: the live endpoint, plus the historical one when the market predates the cutoff."""
    paths = ["markets/trades"] + (["historical/trades"] if close <= hist_cut + pd.Timedelta(days=1) else [])
    seen, out = set(), []
    for path in paths:
        cursor = None
        for _ in range(max_pages):
            p = {"ticker": ticker, "limit": 1000}
            if cursor:
                p["cursor"] = cursor
            r = wx._get(f"{wx.KALSHI}/{path}", p)
            if r is None or r.status_code != 200:
                break
            j = r.json()
            for t in j.get("trades", []):
                k = t.get("trade_id") or (t.get("created_time"), t.get("count_fp"), t.get("yes_price_dollars"))
                if k not in seen:
                    seen.add(k)
                    out.append(t)
            cursor = j.get("cursor")
            if not cursor or not j.get("trades"):
                break
    return out


def market_row(m: dict, tr: list[dict], fee_mult: float) -> dict:
    """What a 99c bid on the winning-looking side would have done in one market."""
    close = pd.to_datetime(m.get("close_time"), utc=True)
    reach = won = 0.0
    first = None
    for t in tr:
        side = t.get("taker_side")
        if side not in ("yes", "no"):
            continue
        pd_ = t.get(f"{side}_price_dollars")
        try:
            px = float(pd_) if pd_ not in (None, "") else float(t.get(f"{side}_price", 100)) / 100
        except (TypeError, ValueError):
            continue
        if not (LO - 1e-9 <= px <= HI + 1e-9):
            continue
        n = float(t.get("count_fp") or t.get("count") or 0)
        reach += n
        if side == m["result"]:
            won += n
        ts = pd.Timestamp(t["created_time"])
        first = ts if first is None or ts < first else first
    ours = min(CAP, CAPTURE * reach)
    lose_share = won / reach if reach else 0.0
    fee = r15._maker_fee(ours, 0.99) * fee_mult if ours > 0 else 0.0
    pnl = ours * ((1 - lose_share) * 0.01 - lose_share * 0.99) - fee
    return {"ticker": m["ticker"], "close": close, "reach": reach, "longshot_won": won, "ours": ours, "pnl": pnl,
            "lead_min": (close - first).total_seconds() / 60 if first is not None else np.nan,
            "structure": m.get("price_level_structure", "")}


def summarize(rows: pd.DataFrame) -> dict:
    f = rows[rows["reach"] > 0]
    w = rows["weight"].iloc[0] if len(rows) else 1
    return {"markets": len(rows), "with_fills": len(f), "reach": f["reach"].sum(),
            "win_rate": f["longshot_won"].sum() / f["reach"].sum() if f["reach"].sum() else np.nan,
            "pnl": f["pnl"].sum(), "pnl_x_weight": f["pnl"].sum() * w, "losing_markets": int((f["pnl"] < 0).sum()),
            "worst": f["pnl"].min() if len(f) else 0.0, "lead_min": f["lead_min"].median(), "weight": w}
