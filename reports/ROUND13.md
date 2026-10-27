# Round 13: stock core + multi-asset trend + crypto trend

Rules: [PROTOCOL_ROUND13.md](../PROTOCOL_ROUND13.md). Out-of-sample 2012-01-03 to 2026-10-27; config re-chosen every 6 months from past data only.

## Verdict: **PASS**

| | Strategy | Buy & hold SPY |
|---|---:|---:|
| $1,000 became | $6,335 | $7,913 |
| Yearly return | +13.3% | +15.0% |
| Sharpe | 1.19 | 0.93 |
| Worst drop | -20.4% | -33.7% |
| Deflated Sharpe (269 trials) | 0.957 | |

| Check | Result |
|---|---|
| sharpe>=1 | yes |
| dsr>=0.95 | yes |
| beats_tbills | yes |
| max_dd<=25% | yes |
| changes>=30 | yes |
| beats_benchmark_sharpe | yes |

## Config chosen at each refit

| Refit | Chosen | Training Sharpe |
|---|---|---:|
| 2012-01-01 | volman-sma50-crypto30-trend40 | 0.56 |
| 2012-07-01 | volman-sma50-crypto30-trend40 | 0.58 |
| 2013-01-01 | volman-sma50-crypto30-trend40 | 0.59 |
| 2013-07-01 | volman-sma50-crypto30-trend40 | 0.63 |
| 2014-01-01 | volman-sma50-crypto30-trend40 | 0.75 |
| 2014-07-01 | volman-sma50-crypto30-trend40 | 0.8 |
| 2015-01-01 | volman-sma50-crypto30-trend40 | 0.83 |
| 2015-07-01 | volman-sma100-crypto30-trend40 | 0.76 |
| 2016-01-01 | volman-sma50-crypto30-trend40 | 0.71 |
| 2016-07-01 | volman-sma50-crypto30-trend40 | 0.83 |
| 2017-01-01 | volman-sma50-crypto30-trend40 | 0.95 |
| 2017-07-01 | volman-sma50-crypto30-trend40 | 1.19 |
| 2018-01-01 | volman-sma50-crypto30-trend40 | 1.39 |
| 2018-07-01 | volman-sma100-crypto30-trend40 | 1.26 |
| 2019-01-01 | volman-sma100-crypto30-trend40 | 1.18 |
| 2019-07-01 | volman-sma100-crypto30-trend40 | 1.35 |
| 2020-01-01 | volman-sma50-crypto30-trend40 | 1.26 |
| 2020-07-01 | volman-sma50-crypto30-trend40 | 1.19 |
| 2021-01-01 | volman-sma50-crypto30-trend40 | 1.36 |
| 2021-07-01 | volman-sma50-crypto30-trend40 | 1.41 |
| 2022-01-01 | volman-sma50-crypto30-trend40 | 1.34 |
| 2022-07-01 | volman-sma100-crypto30-trend40 | 1.24 |
| 2023-01-01 | volman-sma100-crypto30-trend40 | 1.2 |
| 2023-07-01 | volman-sma100-crypto30-trend40 | 1.2 |
| 2024-01-01 | volman-sma100-crypto30-trend40 | 1.19 |
| 2024-07-01 | volman-sma100-crypto30-trend40 | 1.24 |
| 2025-01-01 | volman-sma100-crypto30-trend40 | 1.25 |
| 2025-07-01 | volman-sma100-crypto30-trend40 | 1.2 |
| 2026-01-01 | volman-sma100-crypto30-trend40 | 1.23 |
| 2026-07-01 | volman-sma100-crypto30-trend40 | 1.23 |

## By year (out of sample)

| Year | Return |
|---|---:|
| 2012 | +3.3% |
| 2013 | +10.1% |
| 2014 | +6.7% |
| 2015 | -8.7% |
| 2016 | +27.6% |
| 2017 | +70.0% |
| 2018 | -15.1% |
| 2019 | +22.0% |
| 2020 | +38.9% |
| 2021 | +18.7% |
| 2022 | -11.5% |
| 2023 | +14.0% |
| 2024 | +30.8% |
| 2025 | +12.3% |
| 2026 | +4.2% |
