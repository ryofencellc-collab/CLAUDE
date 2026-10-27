"""Round 9: let the data pick the trade gates (PROTOCOL_ROUND9.md).

A gate is a yes/no per coin per day built only from data up to that close.
The strategy holds an equal weight in every tradable coin whose chosen gates
are all "yes", cash otherwise. The procedure under test picks which gates and
how many from training data only; walk_forward() judges it on unseen blocks.
"""
import numpy as np
import pandas as pd

from edge.backtest import run

COST = 0.001
PERIODS = 365
START = pd.Timestamp("2019-10-01")
FIRST_TEST = pd.Timestamp("2021-01-01")
MAX_GATES = 6
MIN_CHANGES = 60
MIN_USD = 5e6


def base_gates(p: dict, spy: pd.Series | None = None) -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    """The 15 base gates of the protocol: (value, known) bool frames (dates x coins)."""
    px = p["spot_close"]
    idx, cols = px.index, px.columns
    rets = px.pct_change(fill_method=None)
    vol20 = rets.rolling(20, min_periods=15).std()
    vol60 = rets.rolling(60, min_periods=45).std()
    fund = p["funding"].reindex(index=idx, columns=cols)
    f7 = fund.rolling(7, min_periods=5).mean()
    qv = p["spot_qv"].reindex(index=idx, columns=cols)
    perp = p["perp_close"].reindex(index=idx, columns=cols)
    btc = px["BTC"]

    def wide(s):  # one series broadcast to every coin
        return pd.DataFrame(np.repeat(s.to_numpy()[:, None], len(cols), axis=1), index=idx, columns=cols)

    def both(a, b, op):  # comparison plus where both sides are known
        return op(a, b), a.notna() & b.notna()

    gt = lambda a, b: a > b
    lt = lambda a, b: a < b
    zero = pd.DataFrame(0.0, index=idx, columns=cols)
    g = {
        "above_sma50": both(px, px.rolling(50).mean(), gt),
        "above_sma100": both(px, px.rolling(100).mean(), gt),
        "above_sma200": both(px, px.rolling(200).mean(), gt),
        "mom20_up": both(px.pct_change(20, fill_method=None), zero, gt),
        "mom60_up": both(px.pct_change(60, fill_method=None), zero, gt),
        "btc_above_sma100": tuple(map(wide, both(btc, btc.rolling(100).mean(), gt))),
        "vol_below_1y_median": both(vol20, vol20.rolling(365, min_periods=180).median(), lt),
        "vol_falling": both(vol20, vol60, lt),
        "funding_negative": both(f7, zero, lt),
        "funding_below_90d_median": both(f7, f7.rolling(90, min_periods=60).median(), lt),
        "pullback_3d": both(px.pct_change(3, fill_method=None), zero, lt),
        "volume_rising": both(qv.rolling(7).mean(), qv.rolling(30).mean(), gt),
        "perp_discount": both(perp, px, lt),
        "weekday": (wide(pd.Series(idx.dayofweek < 5, index=idx)), wide(pd.Series(True, index=idx))),
    }
    if spy is not None:
        s = spy.reindex(idx, method="ffill")  # weekend: Friday's close is the latest known
        g["spy_above_sma200"] = tuple(map(wide, both(s, spy.rolling(200).mean().reindex(idx, method="ffill"), gt)))
    return g


def gate_library(p: dict, spy: pd.Series | None = None) -> dict[str, np.ndarray]:
    """Both directions of every base gate. Missing inputs make a gate 'no' either way."""
    lib = {}
    for name, (frame, known) in base_gates(p, spy).items():
        val = frame.fillna(False).astype(bool).to_numpy()
        ok = known.fillna(False).astype(bool).to_numpy()
        lib[name] = val & ok
        lib[f"NOT_{name}"] = ~val & ok
    return lib


class Evaluator:
    """Fast net-return evaluation of a gate mask (numpy, same conventions as backtest.run)."""

    def __init__(self, p: dict):
        px = p["spot_close"]
        self.index = px.index
        self.columns = px.columns
        self.R = np.nan_to_num(px.pct_change(fill_method=None).to_numpy(), nan=0.0)
        liquid = p["spot_qv"].reindex(index=px.index, columns=px.columns).rolling(30, min_periods=20).median() > MIN_USD
        self.liquid = (liquid & px.notna()).to_numpy()

    def weights(self, mask: np.ndarray) -> np.ndarray:
        m = mask & self.liquid
        cnt = m.sum(axis=1, keepdims=True)
        return np.divide(m, cnt, out=np.zeros(m.shape), where=cnt > 0)

    def net(self, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        w = self.weights(mask)
        held = np.vstack([np.zeros((1, w.shape[1])), w[:-1]])
        gross = (held * self.R).sum(axis=1)
        turn = np.abs(np.diff(np.vstack([np.zeros((1, w.shape[1])), held]), axis=0)).sum(axis=1)
        return gross - COST * turn, turn

    def score(self, mask: np.ndarray, rows: np.ndarray) -> tuple[float, int]:
        r, t = self.net(mask)
        r, t = r[rows], t[rows]
        sd = r.std()
        return (float(r.mean() / sd * np.sqrt(PERIODS)) if sd > 0 else -9.0), int((t > 1e-9).sum())


def greedy_path(ev: Evaluator, lib: dict, rows: np.ndarray) -> list[str]:
    """Add, one at a time, the gate that most raises training Sharpe (up to MAX_GATES)."""
    mask = np.ones_like(ev.liquid)
    path = []
    for _ in range(MAX_GATES):
        best = None
        for name, g in lib.items():
            if name in path or (name.removeprefix("NOT_") in {x.removeprefix("NOT_") for x in path}):
                continue  # a gate and its opposite never combine
            sh, ch = ev.score(mask & g, rows)
            if ch >= MIN_CHANGES and (best is None or sh > best[0]):
                best = (sh, name)
        if best is None:
            break
        path.append(best[1])
        mask = mask & lib[best[1]]
    return path


def _mask(ev: Evaluator, lib: dict, names: list[str]) -> np.ndarray:
    m = np.ones_like(ev.liquid)
    for n in names:
        m = m & lib[n]
    return m


def select(ev: Evaluator, lib: dict, train_rows: np.ndarray) -> tuple[list[str], dict]:
    """Choose the gates and how many, using the training rows only."""
    pos = np.flatnonzero(train_rows)
    cut = pos[int(len(pos) * 0.75)]
    fit = train_rows.copy()
    fit[cut:] = False
    val = train_rows.copy()
    val[:cut] = False
    path = greedy_path(ev, lib, fit)
    val_sh = [ev.score(_mask(ev, lib, path[:k]), val)[0] for k in range(len(path) + 1)]
    k = int(np.argmax(val_sh))
    full = greedy_path(ev, lib, train_rows)[:k]
    return full, {"inner_path": path, "val_sharpe_by_k": [round(v, 2) for v in val_sh], "k": k}


def refit_dates(index: pd.DatetimeIndex) -> list[pd.Timestamp]:
    out, d = [], FIRST_TEST
    while d <= index[-1]:
        out.append(d)
        d = d + pd.DateOffset(months=6)
    return out


def walk_forward(p: dict, spy: pd.Series | None = None) -> tuple[pd.Series, pd.Series, list[dict]]:
    """Refit every 6 months on an expanding window; trade each block with gates chosen without it."""
    ev = Evaluator(p)
    lib = gate_library(p, spy)
    idx = ev.index
    W = np.zeros(ev.liquid.shape)
    log = []
    dates = refit_dates(idx)
    for i, d in enumerate(dates):
        end = dates[i + 1] if i + 1 < len(dates) else idx[-1] + pd.Timedelta(days=1)
        train = np.asarray((idx >= START) & (idx < d))
        block = np.asarray((idx >= d) & (idx < end))
        gates, info = select(ev, lib, train)
        W[block] = ev.weights(_mask(ev, lib, gates))[block]
        log.append({"refit": d.date().isoformat(), "gates": gates, **info})
        print(f"  refit {d.date()}: {len(gates)} gates {gates}", flush=True)
    res = run(pd.DataFrame(W, index=idx, columns=ev.columns),
              p["spot_close"].pct_change(fill_method=None), COST)
    oos = idx >= FIRST_TEST
    return res.returns[oos], res.turnover[oos], log


def verdict(oos: pd.Series, turnover: pd.Series, btc_close: pd.Series, n_trials: int = 264) -> dict:
    """The six pass conditions of PROTOCOL_ROUND9.md on the out-of-sample series."""
    from edge.backtest import metrics
    from edge.stats import deflated_sharpe
    m = metrics(oos, PERIODS, turnover)
    btc = btc_close.pct_change(fill_method=None).reindex(oos.index).fillna(0.0)
    btc_sh = float(btc.mean() / btc.std() * np.sqrt(PERIODS)) if btc.std() > 0 else 0.0
    dsr = deflated_sharpe(oos, n_trials, 1 / len(oos)) if oos.std() > 0 else 0.0
    checks = {
        "sharpe>=1": m["sharpe"] >= 1.0,
        "dsr>=0.95": dsr >= 0.95,
        "beats_tbills": m["cagr"] > 0.04,
        "max_dd<=25%": m["max_dd"] >= -0.25,
        "changes>=30": m["trades"] >= 30,
        "beats_btc_sharpe": m["sharpe"] > btc_sh,
    }
    return {**m, "dsr": float(dsr), "btc_sharpe": btc_sh, "checks": checks, "pass": all(checks.values())}
