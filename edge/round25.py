"""Round 25 (PROTOCOL_ROUND25.md): confidence-scaled sizing for the 15-minute crypto trade.

1. Reversal model. From Binance 1-minute data, every minute inside every 15-minute window is a sample:
   features of the chart at that minute (seen through the last completed minute only) and whether the side
   that was winning then ended up losing at the close ("flip"). Models: z-bin table, logistic regression,
   gradient-boosted trees (monotone in |z| and time left).
2. Policies. Using Round 21's Kalshi fills (real long-shot trades), each policy decides per fill whether we
   are in and how large our position may be (a fraction of the account). Positions can grow as confidence
   grows (pyramiding), never shrink. One market at a time, $1,000 start, profits compounded.
3. Selection on Apr-Sep 2026 (dev), verdict on Oct 2026 (holdout).
"""
import math

import numpy as np
import pandas as pd

COINS = {"KXBTC15M": "BTCUSDT", "KXETH15M": "ETHUSDT", "KXSOL15M": "SOLUSDT", "KXXRP15M": "XRPUSDT",
         "KXDOGE15M": "DOGEUSDT"}
FEATURES = ["az", "tau", "dist_bp", "mom1", "mom3", "mom5", "volratio", "jump", "hour", "dow", "coin", "logvol"]
CAPTURE = 0.25
PRICE = 0.99
WIN, LOSS = 0.01, 0.99


def fee(n: float) -> float:
    return math.ceil(0.0175 * n * PRICE * (1 - PRICE) * 100 - 1e-9) / 100 if n > 0 else 0.0


# ---------------------------------------------------------------------- features
def frame(spot: pd.Series, coin: int) -> pd.DataFrame:
    """Per minute m (index = close time of minute m): the 15-minute window m belongs to, chart features as of m,
    and the outcome of that window. Only information up to m is used for features."""
    s = spot[~spot.index.duplicated()].sort_index()
    full = pd.date_range(s.index[0], s.index[-1], freq="1min")
    s = s.reindex(full).ffill()
    lr = np.log(s).diff()
    vol60 = lr.rolling(60, min_periods=30).std()
    vol5 = lr.rolling(5, min_periods=5).std()
    t = s.index
    close = t.ceil("15min")
    close = close.where(close != t, t + pd.Timedelta(minutes=15))   # a minute ending exactly on the boundary
    start = close - pd.Timedelta(minutes=15)                          # belongs to the next window
    K = s.reindex(start).to_numpy()
    final = s.reindex(close).to_numpy()
    tau = np.maximum((close - t).total_seconds().to_numpy() / 60, 0.5)
    v = vol60.to_numpy()
    x = np.log(s.to_numpy() / K)
    z = x / (v * np.sqrt(tau))
    side = np.sign(z)                                                  # +1: YES winning, -1: NO winning
    def mom(k):
        return side * (np.log(s / s.shift(k))).to_numpy() / (v * np.sqrt(k))
    jump = (lr.abs().rolling(10, min_periods=1).max() / vol60).to_numpy()
    out = pd.DataFrame({
        "time": t, "close": close, "coin": coin, "z": z, "az": np.abs(z), "tau": tau,
        "dist_bp": np.abs(x) * 1e4, "mom1": mom(1), "mom3": mom(3), "mom5": mom(5),
        "volratio": (vol5 / vol60).to_numpy(), "jump": jump, "hour": t.hour, "dow": t.dayofweek,
        "logvol": np.log(v), "flip": (np.sign(np.log(final / K)) != side) & (final != K)})
    out = out[np.isfinite(out[["z", "mom5", "volratio", "logvol"]]).all(axis=1) & np.isfinite(final)]
    return out


def features_at(spot: pd.Series, coin: int, times: pd.Series) -> pd.DataFrame:
    """Features for arbitrary fill times, through the last completed minute before each time."""
    f = frame(spot, coin).set_index("time")
    idx = f.index.searchsorted(pd.DatetimeIndex(times), side="right") - 1
    ok = idx >= 0
    rows = f.iloc[np.clip(idx, 0, None)].reset_index()
    rows.loc[~ok, FEATURES] = np.nan
    # time left must be measured from the fill itself, not the minute
    rows["tau"] = np.maximum((rows["close"] - pd.DatetimeIndex(times).tz_convert(rows["close"].dt.tz)).total_seconds() / 60, 0.5)
    return rows


# ---------------------------------------------------------------------- models of P(flip)
class ZBins:
    """Empirical flip rate by (|z| bin, minutes-left bin), with a prior so empty cells are not zero."""
    name = "zbins"
    ZB = [0, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 30, 1e9]
    TB = [0, 1, 2, 4, 7, 10, 15]

    def fit(self, d: pd.DataFrame):
        g = d.groupby([pd.cut(d["az"], self.ZB), pd.cut(d["tau"], self.TB)], observed=False)["flip"]
        self.n, self.k = g.size(), g.sum()
        self.rate = (self.k + 0.5) / (self.n + 1.0)                    # Jeffreys-style prior
        return self

    def predict(self, d: pd.DataFrame) -> np.ndarray:
        key = pd.MultiIndex.from_arrays([pd.cut(d["az"], self.ZB), pd.cut(d["tau"], self.TB)])
        return self.rate.reindex(key).to_numpy(dtype=float)


class Logit:
    name = "logit"

    def fit(self, d: pd.DataFrame):
        from sklearn.linear_model import LogisticRegression
        self.m = LogisticRegression(max_iter=500, C=1.0)
        self.m.fit(self._x(d), d["flip"].astype(int))
        return self

    def _x(self, d):
        return np.column_stack([np.log(d["az"]), np.log(d["tau"]), d["mom1"].clip(-10, 10), d["mom3"].clip(-10, 10),
                                d["mom5"].clip(-10, 10), np.log(d["volratio"].clip(0.05, 20)), np.log(d["jump"].clip(0.1, 50)),
                                d["logvol"]])

    def predict(self, d):
        return self.m.predict_proba(self._x(d))[:, 1]


class GBM:
    name = "gbm"

    def fit(self, d: pd.DataFrame):
        from sklearn.ensemble import HistGradientBoostingClassifier
        # monotone: more |z| never raises the flip risk; more time left never lowers it
        cst = [-1 if f == "az" else 1 if f == "tau" else 0 for f in FEATURES]
        self.m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31,
                                                monotonic_cst=cst, categorical_features=[FEATURES.index("coin")])
        self.m.fit(d[FEATURES].to_numpy(dtype=float), d["flip"].astype(int))
        return self

    def predict(self, d):
        return self.m.predict_proba(d[FEATURES].to_numpy(dtype=float))[:, 1]


def calibration(p: np.ndarray, y: np.ndarray, edges=(0, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 1)) -> pd.DataFrame:
    b = pd.cut(p, edges, include_lowest=True)
    t = pd.DataFrame({"bin": b, "p": p, "y": y.astype(float)}).groupby("bin", observed=False)
    return t.agg(n=("y", "size"), predicted=("p", "mean"), actual=("y", "mean"), flips=("y", "sum"))


# ---------------------------------------------------------------------- policies and the account simulator
def kelly_fraction(p: np.ndarray, mult: float, cap: float) -> np.ndarray:
    """Kelly for a bet that wins WIN/PRICE and loses LOSS/PRICE of the stake: f* = (1-p) - p * LOSS / WIN."""
    f = (1 - p) - p * (LOSS / WIN)
    return np.clip(mult * f, 0, cap)


def simulate(fills: pd.DataFrame, frac: np.ndarray, start: float = 1000.0) -> dict:
    """fills: chronological long-shot trades (columns ticker, time, close, count, ours_won); frac: the policy's
    allowed position at each fill as a share of the account (0 = out). One market at a time; position may grow
    with later fills, never shrink. Returns the account path and stats."""
    bal, peak, maxdd = start, start, 0.0
    active, held, cost_fee, losses, markets, worst = None, 0.0, 0.0, 0, 0, 0.0
    path = []

    def settle():
        nonlocal bal, held, active, cost_fee, losses, markets, worst, peak, maxdd
        if active is None:
            return
        won = active["won"]
        pnl = held * (WIN if won else -LOSS) - cost_fee
        if held > 0:
            markets += 1
            losses += 0 if won else 1
            worst = min(worst, pnl / max(bal, 1e-9))
        bal += pnl
        peak = max(peak, bal)
        maxdd = min(maxdd, bal / peak - 1)
        path.append((active["close"], bal))
        active, held, cost_fee = None, 0.0, 0.0

    for (t, ticker, close, count, won), f in zip(fills[["time", "ticker", "close", "count", "ours_won"]].itertuples(index=False), frac):
        if active is not None and t >= active["close"]:
            settle()
        if active is not None and ticker != active["ticker"]:
            continue                                   # busy with another market
        if not (f > 0) or bal <= 1:
            continue
        cap = math.floor(f * bal / PRICE)
        add = min(CAPTURE * count, max(0.0, cap - held))
        if add <= 0:
            continue
        if active is None:
            active = {"ticker": ticker, "close": close, "won": won}
        held += add
        cost_fee += fee(add)
    settle()
    days = max((fills["time"].max() - fills["time"].min()).total_seconds() / 86400, 1e-9) if len(fills) else 1
    growth = (bal / start) ** (1 / days) - 1 if bal > 0 else -1
    return {"final": bal, "max_dd": maxdd, "markets": markets, "losses": losses, "worst_trade": worst,
            "daily_growth": growth, "days_to_10k": (math.log(10) / math.log(1 + growth)) if growth > 0 else math.inf,
            "path": path}


def expected_log_growth(fills: pd.DataFrame, frac: np.ndarray, p: np.ndarray) -> float:
    """Model-based score: sum over fills taken of E[log(1 + position return)] under the predicted flip risk,
    so a policy cannot win selection just because no flip happened to occur in the sample."""
    take = frac > 0
    f = frac[take]
    q = np.clip(p[take], 1e-7, 0.5)
    w = (1 - q) * np.log1p(f * WIN / PRICE) + q * np.log1p(-np.minimum(f * LOSS / PRICE, 0.999999))
    return float(w.sum())
