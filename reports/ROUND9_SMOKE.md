# Round 9 SMOKE TEST (3 coins, pipeline check, not a result): data-chosen trade gates

Rules: [PROTOCOL_ROUND9.md](../PROTOCOL_ROUND9.md). Out-of-sample = every 6-month block traded with gates chosen without it, 2021-01-01 to 2026-09-30.

## Verdict: **FAIL**

| | Gate strategy | Buy & hold BTC |
|---|---:|---:|
| $1,000 became | $1,656 | $2,891 |
| Yearly return | +9.2% | +20.3% |
| Sharpe | 0.45 | 0.61 |
| Worst drop | -81.5% | -76.6% |
| Deflated Sharpe (264 trials) | 0.038 | |
| Days with a position change | 189 | |

| Check | Result |
|---|---|
| sharpe>=1 | **no** |
| dsr>=0.95 | **no** |
| beats_tbills | yes |
| max_dd<=25% | **no** |
| changes>=30 | yes |
| beats_btc_sharpe | **no** |

## What the data chose at each refit

| Refit | # gates | Gates | Validation Sharpe by # gates (0, 1, 2, ...) |
|---|---:|---|---|
| 2021-01-01 | 1 | perp_discount | [4.06, 4.79, 3.82, 2.94] |
| 2021-07-01 | 0 | (none: hold all) | [3.11, 0.06, -0.26, -0.89, -0.42] |
| 2022-01-01 | 0 | (none: hold all) | [2.14, 1.97, 0.47, 1.91, 1.91, 1.49, 1.57] |
| 2022-07-01 | 4 | above_sma50, btc_above_sma100, spy_above_sma200, NOT_funding_negative | [-1.94, -1.2, 0.15, 0.04, 0.2, 0.2, 0.2] |
| 2023-01-01 | 6 | above_sma50, btc_above_sma100, spy_above_sma200, NOT_funding_negative, mom60_up, above_sma100 | [-1.38, -1.81, -1.26, -0.83, -0.59, -0.59, -0.12] |
| 2023-07-01 | 2 | above_sma50, btc_above_sma100 | [0.34, 0.27, 0.39, 0.38, 0.04, -0.09, -0.09] |
| 2024-01-01 | 0 | (none: hold all) | [2.4, 0.68, 0.55, -0.05, -0.34, -0.29, -0.2] |
| 2024-07-01 | 0 | (none: hold all) | [2.09, 2.06, 2.06, 1.88, 1.71, 1.27, 1.28] |
| 2025-01-01 | 5 | btc_above_sma100, volume_rising, mom60_up, NOT_funding_negative, spy_above_sma200 | [2.21, 1.72, 2.08, 1.93, 1.81, 2.47, 2.28] |
| 2025-07-01 | 3 | btc_above_sma100, volume_rising, mom60_up | [1.01, 0.79, 1.04, 1.59, 1.56, 1.51, 1.57] |
| 2026-01-01 | 3 | btc_above_sma100, volume_rising, mom60_up | [0.3, 0.26, 0.53, 0.75, 0.71, 0.66, 0.72] |
| 2026-07-01 | 2 | btc_above_sma100, volume_rising | [-0.11, 0.63, 0.92, 0.78, 0.88, 0.79, 0.74] |
