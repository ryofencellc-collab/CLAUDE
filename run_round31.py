"""Round 31 runner (PROTOCOL_ROUND31.md).
python run_round31.py data SERIES   -> data/r31/SERIES_{meta,quotes,spot}.pkl
python run_round31.py run           -> reports/ROUND31.md"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA, OUT = Path("data/r31"), Path("reports/ROUND31.md")
A, B, SPLIT = pd.Timestamp("2025-07-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC"), pd.Timestamp("2026-05-01", tz="UTC")
STAKE = 10.0


def data(series: str):
    from edge import round21, round31
    DATA.mkdir(parents=True, exist_ok=True)
    meta, quotes = round31.fetch(series, A, B, SPLIT)
    spot = round21.minutes(round31.SERIES[series], A - pd.Timedelta(days=2), B)
    meta.to_pickle(DATA / f"{series}_meta.pkl")
    quotes.to_pickle(DATA / f"{series}_quotes.pkl")
    spot.to_pickle(DATA / f"{series}_spot.pkl")
    print(f"{series}: {len(meta)} markets, {len(quotes)} quote minutes, {len(spot)} spot minutes", flush=True)


# ------------------------------------------------------------------ panel
def rsi(c, n):
    d = c.diff()
    up, dn = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(), (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def panel(series: str) -> pd.DataFrame:
    meta = pd.read_pickle(DATA / f"{series}_meta.pkl")
    q = pd.read_pickle(DATA / f"{series}_quotes.pkl")
    spot = pd.read_pickle(DATA / f"{series}_spot.pkl")
    spot = spot[~spot.index.duplicated()].asfreq("1min").ffill()
    lr = np.log(spot).diff()
    feat = pd.DataFrame({"spot": spot, "sig": lr.rolling(60, min_periods=40).std(), "rsi2": rsi(spot, 2) / 100 - 0.5,
                         "rsi7": rsi(spot, 7) / 100 - 0.5, "mom3": np.log(spot).diff(3), "mom5": np.log(spot).diff(5),
                         "ema_gap": (spot.ewm(span=9).mean() - spot.ewm(span=21).mean()) / spot})
    d = q.merge(meta, on="ticker", how="inner")
    d = d[(d["t"] > d["open"]) & (d["t"] < d["close"])].copy()
    d = d.join(feat, on="t")
    d["k"] = ((d["t"] - d["open"]).dt.total_seconds() / 60).round().astype(int)
    d["tau"] = (d["close"] - d["t"]).dt.total_seconds() / 60
    d["z"] = np.log(d["spot"] / d["strike"]) / (d["sig"] * np.sqrt(d["tau"]))
    d["mid"] = (d["bid"] + d["ask"]) / 2
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=["bid", "ask", "z", "rsi7", "mom5"])
    d = d[(d["ask"] > d["bid"]) & (d["ask"] <= 1) & (d["bid"] >= 0)]
    d = d.sort_values(["ticker", "t"])
    # later-minute trade lows/highs (for maker fills): min trade price after this minute, before close
    d["fut_px_low"] = d.groupby("ticker")["px_low"].transform(lambda s: s[::-1].cummin()[::-1].shift(-1))
    d["fut_px_high"] = d.groupby("ticker")["px_high"].transform(lambda s: s[::-1].cummax()[::-1].shift(-1))
    d["mid_chg2"] = d.groupby("ticker")["mid"].diff(2)
    d["series"] = series
    return d


def taker_fee(p, c):
    return np.ceil(0.07 * c * p * (1 - p) * 100 - 1e-9) / 100


def maker_fee(p, c):
    return np.ceil(0.0175 * c * p * (1 - p) * 100 - 1e-9) / 100


def settle(d: pd.DataFrame, side: pd.Series, price: pd.Series, maker: bool = False, fill: pd.Series | None = None) -> pd.DataFrame:
    """One bet per market: the first row where side is set (and filled, for makers)."""
    m = side.notna() & price.between(0.01, 0.99)
    if fill is not None:
        m &= fill
    x = d[m].assign(side=side[m], price=price[m]).groupby("ticker", sort=False).head(1)
    c = STAKE / x["price"]
    won = np.where(x["side"] == "yes", x["up"] == 1, x["up"] == 0)
    fee = (maker_fee if maker else taker_fee)(x["price"].to_numpy(), c.to_numpy())
    return pd.DataFrame({"t": x["t"].to_numpy(), "pnl": c.to_numpy() * (won.astype(float) - x["price"].to_numpy()) - fee})


def theories(d: pd.DataFrame, fair: pd.Series, fair_b: pd.Series, up_hours: set) -> dict:
    yes_ask, no_ask = d["ask"], 1 - d["bid"]
    out = {}
    nan = pd.Series(np.nan, index=d.index, dtype=object)

    def pick(cond_yes, cond_no):
        s = nan.copy()
        s[cond_no] = "no"
        s[cond_yes] = "yes"
        return s

    def price_for(side):
        return pd.Series(np.where(side == "yes", yes_ask, no_ask), index=d.index)

    for name, f in (("T1 fair gap taker", fair), ("T3 indicator gap taker", fair_b)):
        for m in ((0.03, 0.05, 0.08, 0.12) if name.startswith("T1") else (0.03, 0.05)):
            s = pick(f - yes_ask > m, (1 - f) - no_ask > m)
            out[f"{name} {int(m*100)}c"] = settle(d, s, price_for(s))
    for name, f in (("T2 fair gap maker", fair), ("T3 indicator gap maker", fair_b)):
        for m in ((0.02, 0.04, 0.06) if name.startswith("T2") else (0.02, 0.04)):
            yb, nb = (f - m).round(2), ((1 - f) - m).round(2)
            # rest the bid only if it is below the current ask (a maker order); filled if later trades go through it
            s = pick((yb < yes_ask) & (yb > d["bid"]), (nb < no_ask) & (nb > 1 - d["ask"]))
            px = pd.Series(np.where(s == "yes", yb, nb), index=d.index)
            fill = pd.Series(np.where(s == "yes", d["fut_px_low"] <= yb - 0.01, (1 - d["fut_px_high"]) <= nb - 0.01), index=d.index)
            out[f"{name} {int(m*100)}c"] = settle(d, s, px, maker=True, fill=fill)
    fav_yes = d["mid"] >= 0.5
    for lo, hi in ((0.80, 0.90), (0.90, 0.95), (0.95, 0.99)):
        for k in (5, 10, 13):
            s = pick(fav_yes & yes_ask.between(lo, hi - 1e-9) & (d["k"] >= k), ~fav_yes & no_ask.between(lo, hi - 1e-9) & (d["k"] >= k))
            out[f"T4 favourite {int(lo*100)}-{int(hi*100)}c from min {k}"] = settle(d, s, price_for(s))
    for cmax in (0.03, 0.05, 0.10):
        for k in (5, 10):
            s = pick(~fav_yes & (yes_ask <= cmax) & (d["k"] >= k), fav_yes & (no_ask <= cmax) & (d["k"] >= k))
            out[f"T5 long shot <= {int(cmax*100)}c from min {k}"] = settle(d, s, price_for(s))
    for dd in (0.05, 0.10):
        early = (d["k"] == 2) & (d["z"].abs() < 0.3)
        s = pick(early & (d["mid"] <= 0.5 - dd), early & (d["mid"] >= 0.5 + dd))
        out[f"T6 fade early move {int(dd*100)}c"] = settle(d, s, price_for(s))
    for dd in (0.10, 0.20):
        s = pick(d["mid_chg2"] >= dd, d["mid_chg2"] <= -dd)
        out[f"T7 chase 2-min jump {int(dd*100)}c"] = settle(d, s, price_for(s))
        s = pick(d["mid_chg2"] <= -dd, d["mid_chg2"] >= dd)
        out[f"T7 fade 2-min jump {int(dd*100)}c"] = settle(d, s, price_for(s))
    s = pick((d["k"] == 1) & d["open"].dt.hour.isin(up_hours), pd.Series(False, index=d.index))
    out["T8 time-of-day up hours"] = settle(d, s, price_for(s))
    mid_ok = d["mid"].between(0.2, 0.8)
    s = pick(mid_ok & (d["rsi2"] < -0.4), mid_ok & (d["rsi2"] > 0.4))
    out["T9 RSI2 reversal"] = settle(d, s, price_for(s))
    s = pick(mid_ok & (d["rsi2"] > 0.4), mid_ok & (d["rsi2"] < -0.4))
    out["T9 RSI2 trend"] = settle(d, s, price_for(s))
    if "btc_dz" in d:
        for th in (0.5, 1.0):
            lag = d["mid_chg1"].abs() < 0.02
            s = pick(lag & (d["btc_dz"] >= th) & mid_ok, lag & (d["btc_dz"] <= -th) & mid_ok)
            out[f"T10 cross-coin lead {th}"] = settle(d, s, price_for(s))
    return out


def run():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    have = [p.name.split("_meta")[0] for p in DATA.glob("*_meta.pkl")]
    d = pd.concat([panel(s) for s in sorted(have)], ignore_index=True)
    d["mid_chg1"] = d.groupby("ticker")["mid"].diff(1)
    if "KXBTC15M" in have:
        btc = d[d["series"] == "KXBTC15M"][["t", "z"]].drop_duplicates("t").set_index("t")["z"].sort_index()
        d["btc_dz"] = d["t"].map(btc.diff())
        d.loc[d["series"] == "KXBTC15M", "btc_dz"] = np.nan
    dev = d[d["close"] < SPLIT]
    xa = lambda x: np.column_stack([x["z"], x["z"] ** 3 / 10, x["k"]])
    fe = ["rsi2", "rsi7", "mom3", "mom5", "ema_gap"]
    xb = lambda x: np.column_stack([xa(x), x[fe].fillna(0).to_numpy()])
    one = dev.groupby("ticker").sample(n=1, random_state=0) if len(dev) else dev
    mA = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(xa(dev), dev["up"])
    mB = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(xb(dev), dev["up"])
    fair = pd.Series(mA.predict_proba(xa(d))[:, 1], index=d.index)
    fair_b = pd.Series(mB.predict_proba(xb(d))[:, 1], index=d.index)
    first = dev[dev["k"] == 1]
    rate = first.groupby(first["open"].dt.hour)["up"].mean()
    up_hours = set(rate[rate > 0.53].index)
    res = theories(d, fair, fair_b, up_hours)
    rows = []
    for name, r in res.items():
        rd, rh = r[r["t"] < SPLIT], r[r["t"] >= SPLIT]
        days_h = max((B - SPLIT).days, 1)
        t = rh["pnl"].mean() / (rh["pnl"].std() / math.sqrt(len(rh))) if len(rh) > 2 and rh["pnl"].std() > 0 else 0.0
        ok = rd["pnl"].sum() > 0 and rh["pnl"].sum() > 0 and len(rh) >= 200 and t >= 3.0
        rows.append({"theory": name, "dev bets": len(rd), "dev $": round(rd["pnl"].sum(), 2), "hold bets": len(rh),
                     "hold $": round(rh["pnl"].sum(), 2), "hold $/day ($10 bets)": round(rh["pnl"].sum() / days_h, 2),
                     "hold win %": round(100 * (rh["pnl"] > 0).mean(), 1) if len(rh) else np.nan,
                     "t-stat": round(t, 2), "PASS": "yes" if ok else "no"})
    tab = pd.DataFrame(rows).sort_values("hold $", ascending=False)
    cal = d[d["close"] >= SPLIT].assign(b=lambda x: (x["mid"] * 20).round() / 20).groupby("b")["up"].agg(["mean", "size"])
    lines = ["# Round 31: theory factory on Kalshi 15-minute crypto markets (real quotes)", "",
             "Rules: [PROTOCOL_ROUND31.md](../PROTOCOL_ROUND31.md). $10 per bet, one bet per market, Kalshi fees.", "",
             f"Markets: {d['ticker'].nunique():,} ({', '.join(f'{s} {n:,}' for s, n in d.groupby('series')['ticker'].nunique().items())}); "
             f"quote-minutes: {len(d):,}. Dev < {SPLIT.date()} ≤ holdout.", "",
             f"**{(tab['PASS'] == 'yes').sum()} of {len(tab)} theories pass.**", "", tab.to_markdown(index=False), "",
             "## Is Kalshi's price honest? (holdout: mid price bucket vs how often YES won)", "",
             cal.rename(columns={"mean": "YES won", "size": "minutes"}).round(3).to_markdown()]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    data(sys.argv[2]) if sys.argv[1] == "data" else run()
