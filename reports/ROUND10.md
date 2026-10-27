# Round 10: crypto trend + volatility limit

Rules: [PROTOCOL_ROUND10.md](../PROTOCOL_ROUND10.md). Out-of-sample 2021-01-01 to 2026-09-30; config re-chosen every 6 months from past data only.

## Verdict: **FAIL**

| | Strategy | Buy & hold BTC |
|---|---:|---:|
| $1,000 became | $2,449 | $2,891 |
| Yearly return | +16.9% | +20.3% |
| Sharpe | 0.85 | 0.61 |
| Worst drop | -33.7% | -76.6% |
| Deflated Sharpe (266 trials) | 0.204 | |

| Check | Result |
|---|---|
| sharpe>=1 | **no** |
| dsr>=0.95 | **no** |
| beats_tbills | yes |
| max_dd<=25% | **no** |
| changes>=30 | yes |
| beats_benchmark_sharpe | yes |

## Config chosen at each refit

| Refit | Chosen | Training Sharpe |
|---|---|---:|
| 2021-01-01 | BTC+ETH-sma50-nogate-vol30 | 3.02 |
| 2021-07-01 | BTC+ETH-sma50-nogate-vol30 | 2.93 |
| 2022-01-01 | BTC+ETH-sma50-nogate-vol30 | 2.62 |
| 2022-07-01 | BTC+ETH-sma50-nogate-vol30 | 2.12 |
| 2023-01-01 | all-sma100-gate-vol20 | 1.75 |
| 2023-07-01 | BTC+ETH-sma50-nogate-vol20 | 1.83 |
| 2024-01-01 | BTC+ETH-sma50-nogate-vol20 | 1.84 |
| 2024-07-01 | BTC+ETH-sma50-nogate-vol20 | 1.87 |
| 2025-01-01 | BTC+ETH-sma50-nogate-vol20 | 1.75 |
| 2025-07-01 | BTC+ETH-sma50-nogate-vol20 | 1.66 |
| 2026-01-01 | BTC+ETH-sma50-gate-vol30 | 1.59 |
| 2026-07-01 | BTC+ETH-sma50-gate-vol40 | 1.44 |

## By year (out of sample)

| Year | Return |
|---|---:|
| 2021 | +62.5% |
| 2022 | -24.3% |
| 2023 | +22.1% |
| 2024 | +29.1% |
| 2025 | +7.8% |
| 2026 | +17.1% |
