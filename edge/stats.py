"""Statistics that guard against fooling ourselves.

Deflated Sharpe Ratio: Bailey & Lopez de Prado (2014), "The Deflated Sharpe
Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality".
"""
from statistics import NormalDist

import numpy as np
import pandas as pd

N = NormalDist()
EULER = 0.5772156649


def _moments(r: pd.Series):
    r = r.dropna().to_numpy()
    sr = r.mean() / r.std(ddof=1)
    z = (r - r.mean()) / r.std(ddof=0)
    return sr, float((z ** 3).mean()), float((z ** 4).mean()), len(r)


def probabilistic_sharpe(r: pd.Series, sr_benchmark: float = 0.0) -> float:
    """P(true per-period Sharpe > sr_benchmark), non-annualised inputs."""
    sr, skew, kurt, n = _moments(r)
    denom = np.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr ** 2, 1e-12))
    return N.cdf((sr - sr_benchmark) * np.sqrt(n - 1) / denom)


def expected_max_sharpe(n_trials: int, var_trial_sr: float) -> float:
    """Expected max per-period Sharpe among n_trials skill-less strategies."""
    if n_trials <= 1:
        return 0.0
    return np.sqrt(var_trial_sr) * (
        (1 - EULER) * N.inv_cdf(1 - 1 / n_trials)
        + EULER * N.inv_cdf(1 - 1 / (n_trials * np.e))
    )


def deflated_sharpe(r: pd.Series, n_trials: int, var_trial_sr: float) -> float:
    return probabilistic_sharpe(r, expected_max_sharpe(n_trials, var_trial_sr))


def block_bootstrap_total(r: pd.Series, horizon: int, n_boot: int = 5000,
                          block: int = 10, seed: int = 0) -> np.ndarray:
    """Distribution of compounded return over `horizon` days (paper-trade band)."""
    rng = np.random.default_rng(seed)
    x = r.dropna().to_numpy()
    out = np.empty(n_boot)
    for i in range(n_boot):
        idx = []
        while len(idx) < horizon:
            s = rng.integers(0, len(x) - block)
            idx.extend(range(s, s + block))
        out[i] = np.prod(1 + x[idx[:horizon]]) - 1
    return out
