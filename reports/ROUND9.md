# Round 9: data-chosen trade gates

Rules: [PROTOCOL_ROUND9.md](../PROTOCOL_ROUND9.md). Out-of-sample = every 6-month block traded with gates chosen without it, 2021-01-01 to 2026-09-30.

## Verdict: **FAIL**

| | Gate strategy | Buy & hold BTC |
|---|---:|---:|
| $1,000 became | $13,052 | $2,891 |
| Yearly return | +56.3% | +20.3% |
| Sharpe | 0.89 | 0.61 |
| Worst drop | -58.7% | -76.6% |
| Deflated Sharpe (264 trials) | 0.201 | |
| Days with a position change | 513 | |

| Check | Result |
|---|---|
| sharpe>=1 | **no** |
| dsr>=0.95 | **no** |
| beats_tbills | yes |
| max_dd<=25% | **no** |
| changes>=30 | yes |
| beats_btc_sharpe | yes |

## What the data chose at each refit

| Refit | # gates | Gates | Validation Sharpe by # gates (0, 1, 2, ...) |
|---|---:|---|---|
| 2021-01-01 | 5 | perp_discount, mom20_up, above_sma200, NOT_vol_below_1y_median, above_sma50 | [1.82, 1.48, 2.19, 2.67, 2.77, 2.94, 2.58] |
| 2021-07-01 | 4 | btc_above_sma100, NOT_vol_falling, above_sma50, NOT_pullback_3d | [2.94, 3.04, 2.99, 3.06, 3.07, 2.72, 2.72] |
| 2022-01-01 | 6 | NOT_vol_falling, btc_above_sma100, NOT_pullback_3d, above_sma100, spy_above_sma200, mom20_up | [1.07, 1.22, 0.85, 0.69, 1.25, 1.25, 1.31] |
| 2022-07-01 | 6 | btc_above_sma100, NOT_pullback_3d, mom20_up, mom60_up, spy_above_sma200, NOT_vol_falling | [-1.84, -2.04, -1.17, -1.23, -0.95, -0.59, -0.46] |
| 2023-01-01 | 0 | (none: hold all) | [-1.14, -1.34, -1.48, -1.69, -2.25, -1.88, -1.88] |
| 2023-07-01 | 0 | (none: hold all) | [0.07, -0.13, -0.7, -0.32, -0.37, -0.34, -0.15] |
| 2024-01-01 | 1 | btc_above_sma100 | [1.1, 1.11, 0.57, 1.06, 0.87, 0.53, 1.09] |
| 2024-07-01 | 0 | (none: hold all) | [0.65, 0.55, -0.17, 0.2, 0.18, 0.06, 0.15] |
| 2025-01-01 | 0 | (none: hold all) | [1.56, 1.43, 1.5, 1.11, 1.15, -0.22, -0.09] |
| 2025-07-01 | 2 | btc_above_sma100, above_sma50 | [0.58, 0.48, 0.73, 0.6, 0.51, -0.36, -0.16] |
| 2026-01-01 | 2 | btc_above_sma100, above_sma50 | [0.29, 0.32, 0.55, 0.36, 0.53, 0.53, 0.25] |
| 2026-07-01 | 5 | btc_above_sma100, above_sma50, NOT_pullback_3d, mom60_up, mom20_up | [0.04, 0.53, 0.91, 0.75, 0.77, 1.32, 1.27] |
