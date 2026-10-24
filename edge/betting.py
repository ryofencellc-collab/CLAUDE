"""Football betting data (football-data.co.uk) and the two Round 2 families.

Column notes (football-data.co.uk/notes.txt):
  FTR            full-time result H/D/A
  PSH/PSD/PSA    Pinnacle pre-match odds (collected with the market max odds)
  PSCH/PSCD/PSCA Pinnacle closing odds
  MaxH/MaxD/MaxA market max pre-match odds (2019/20 on)
  BbMxH/...      Betbrain max pre-match odds (to 2018/19)
"""
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

CACHE = Path(__file__).resolve().parent.parent / "data"
CACHE.mkdir(exist_ok=True)
DIVS = ["E0", "E1", "E2", "E3", "EC", "SC0", "SC1", "SC2", "SC3", "D1", "D2", "I1", "I2",
        "SP1", "SP2", "F1", "F2", "N1", "B1", "P1", "T1", "G1"]
SEASONS = [f"{y % 100:02d}{(y + 1) % 100:02d}" for y in range(2012, 2026)]
HOLDOUT_FROM = "2223"  # seasons 2022/23 onward
SIDES = ("H", "D", "A")


def _get(args):
    season, div = args
    url = f"https://www.football-data.co.uk/mmz4281/{season}/{div}.csv"
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException:
        return None
    if r.status_code != 200 or len(r.content) < 200:
        return None
    df = pd.read_csv(io.BytesIO(r.content), encoding="latin-1", on_bad_lines="skip")
    df["season"], df["div"] = season, div
    return df


def matches(refresh: bool = False) -> pd.DataFrame:
    path = CACHE / "football.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    jobs = [(s, d) for s in SEASONS for d in DIVS]
    with ThreadPoolExecutor(8) as ex:
        parts = [p for p in ex.map(_get, jobs) if p is not None]
    df = pd.concat(parts, ignore_index=True)
    for s in SIDES:
        mx = df.get(f"Max{s}")
        bb = df.get(f"BbMx{s}")
        df[f"best{s}"] = mx.fillna(bb) if mx is not None and bb is not None else (mx if mx is not None else bb)
    keep = ["season", "div", "Date", "HomeTeam", "AwayTeam", "FTR"] + \
           [f"{p}{s}" for p in ("PS", "PSC", "best") for s in SIDES]
    df = df[[c for c in keep if c in df.columns]].dropna(subset=["FTR"])
    for c in df.columns[6:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")  # a few files have stray text
    df.to_pickle(path)
    print(f"football: {len(df)} matches, {df['season'].nunique()} seasons, {df['div'].nunique()} leagues")
    return df


def _long(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (match, outcome)."""
    rows = []
    for s in SIDES:
        rows.append(pd.DataFrame({
            "season": df["season"], "side": s, "won": (df["FTR"] == s).astype(float),
            "ps": df[f"PS{s}"], "psc": df[f"PSC{s}"], "best": df[f"best{s}"],
            "ps_book": sum(1 / df[f"PS{x}"] for x in SIDES),
            "psc_book": sum(1 / df[f"PSC{x}"] for x in SIDES),
        }))
    return pd.concat(rows, ignore_index=True)


def value_vs_pinnacle(df, edge, max_odds):
    """Bet at the best market price when it beats de-vigged Pinnacle by `edge`."""
    x = _long(df).dropna(subset=["ps", "best"])
    fair_odds = x["ps"] * x["ps_book"]  # 1 / (implied / overround)
    pick = (x["best"] >= fair_odds * (1 + edge)) & (x["best"] <= (max_odds or np.inf))
    b = x[pick]
    return pd.DataFrame({"season": b["season"], "ret": b["won"] * b["best"] - 1, "odds": b["best"]})


def favourite_bias(df, cap):
    """Bet every outcome priced <= cap at Pinnacle's closing price."""
    x = _long(df).dropna(subset=["psc"])
    b = x[x["psc"] <= cap]
    return pd.DataFrame({"season": b["season"], "ret": b["won"] * b["psc"] - 1, "odds": b["psc"]})


FAMILIES = {
    "value_vs_pinnacle": (value_vs_pinnacle, [dict(edge=e, max_odds=m)
                                              for e in (0.02, 0.05, 0.10) for m in (None, 5.0)]),
    "favourite_bias": (favourite_bias, [dict(cap=c) for c in (1.3, 1.5, 2.0)]),
}


def bootstrap_p(ret: pd.Series, n_boot: int = 20000, seed: int = 0) -> float:
    """One-sided p-value that mean return <= 0."""
    x = ret.to_numpy()
    if len(x) < 2:
        return 1.0
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), (n_boot, len(x)))].mean(axis=1) if len(x) < 20000 else \
        np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(2000)])
    return float((means <= 0).mean())
