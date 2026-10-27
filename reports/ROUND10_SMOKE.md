# Round 10 SMOKE TEST (3 coins, not a result): crypto trend + volatility limit

Rules: [PROTOCOL_ROUND10.md](../PROTOCOL_ROUND10.md). Out-of-sample 2021-01-01 to 2026-09-30; config re-chosen every 6 months from past data only.

## Verdict: **FAIL**

| | Strategy | Buy & hold BTC |
|---|---:|---:|
| $1,000 became | $6,451 | $2,891 |
| Yearly return | +38.3% | +20.3% |
| Sharpe | 1.23 | 0.61 |
| Worst drop | -40.5% | -76.6% |
| Deflated Sharpe (266 trials) | 0.535 | |

| Check | Result |
|---|---|
| sharpe>=1 | yes |
| dsr>=0.95 | **no** |
| beats_tbills | yes |
| max_dd<=25% | **no** |
| changes>=30 | yes |
| beats_benchmark_sharpe | yes |

## Config chosen at each refit

| Refit | Chosen | Training Sharpe |
|---|---|---:|
| 2021-01-01 | BTC+ETH-sma50-nogate-vol30 | 3.02 |
| 2021-07-01 | top5-sma50-nogate-vol40 | 3.21 |
| 2022-01-01 | top5-sma50-nogate-vol40 | 3.23 |
| 2022-07-01 | top5-sma50-gate-vol40 | 2.69 |
| 2023-01-01 | top5-sma100-nogate-vol20 | 2.11 |
| 2023-07-01 | top5-sma50-nogate-vol40 | 2.14 |
| 2024-01-01 | top5-sma50-nogate-vol40 | 2.38 |
| 2024-07-01 | top5-sma50-nogate-vol40 | 2.28 |
| 2025-01-01 | top5-sma50-nogate-vol40 | 2.12 |
| 2025-07-01 | top5-sma50-nogate-vol40 | 1.99 |
| 2026-01-01 | top5-sma50-nogate-vol40 | 1.89 |
| 2026-07-01 | top5-sma50-nogate-vol40 | 1.73 |

## By year (out of sample)

| Year | Return |
|---|---:|
| 2021 | +130.4% |
| 2022 | -31.7% |
| 2023 | +120.2% |
| 2024 | +42.5% |
| 2025 | +12.6% |
| 2026 | +16.0% |
