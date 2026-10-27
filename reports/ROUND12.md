# Round 12: stock core plus crypto trend sleeve

Rules: [PROTOCOL_ROUND12.md](../PROTOCOL_ROUND12.md). Out-of-sample 2016-01-04 to 2026-10-27; config re-chosen every 6 months from past data only.

## Verdict: **FAIL**

| | Strategy | Buy & hold SPY |
|---|---:|---:|
| $1,000 became | $6,434 | $4,489 |
| Yearly return | +18.8% | +14.9% |
| Sharpe | 1.28 | 0.88 |
| Worst drop | -24.9% | -33.7% |
| Deflated Sharpe (268 trials) | 0.905 | |

| Check | Result |
|---|---|
| sharpe>=1 | yes |
| dsr>=0.95 | **no** |
| beats_tbills | yes |
| max_dd<=25% | yes |
| changes>=30 | yes |
| beats_benchmark_sharpe | yes |

## Config chosen at each refit

| Refit | Chosen | Training Sharpe |
|---|---|---:|
| 2016-01-01 | hold-sma50-crypto30 | 0.78 |
| 2016-07-01 | hold-sma50-crypto30 | 1.0 |
| 2017-01-01 | hold-sma50-crypto30 | 1.35 |
| 2017-07-01 | trend200-sma50-crypto30 | 1.84 |
| 2018-01-01 | trend200-sma50-crypto30 | 2.19 |
| 2018-07-01 | trend200-sma100-crypto30 | 1.87 |
| 2019-01-01 | trend200-sma100-crypto30 | 1.68 |
| 2019-07-01 | volman-sma100-crypto30 | 1.91 |
| 2020-01-01 | volman-sma100-crypto30 | 1.72 |
| 2020-07-01 | volman-sma50-crypto30 | 1.49 |
| 2021-01-01 | volman-sma50-crypto30 | 1.74 |
| 2021-07-01 | volman-sma50-crypto30 | 1.8 |
| 2022-01-01 | volman-sma50-crypto30 | 1.71 |
| 2022-07-01 | trend200-sma100-crypto30 | 1.49 |
| 2023-01-01 | trend200-sma100-crypto30 | 1.42 |
| 2023-07-01 | volman-sma100-crypto30 | 1.44 |
| 2024-01-01 | volman-sma100-crypto30 | 1.43 |
| 2024-07-01 | volman-sma100-crypto30 | 1.51 |
| 2025-01-01 | volman-sma100-crypto30 | 1.51 |
| 2025-07-01 | volman-sma100-crypto30 | 1.42 |
| 2026-01-01 | volman-sma100-crypto30 | 1.44 |
| 2026-07-01 | volman-sma100-crypto30 | 1.43 |

## By year (out of sample)

| Year | Return |
|---|---:|
| 2016 | +31.0% |
| 2017 | +74.4% |
| 2018 | -11.4% |
| 2019 | +20.4% |
| 2020 | +27.9% |
| 2021 | +26.4% |
| 2022 | -18.0% |
| 2023 | +18.3% |
| 2024 | +39.9% |
| 2025 | +11.8% |
| 2026 | +7.5% |
