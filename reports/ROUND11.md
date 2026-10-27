# Round 11: multi-asset trend with risk balancing

Rules: [PROTOCOL_ROUND11.md](../PROTOCOL_ROUND11.md). Out-of-sample 2012-01-03 to 2026-10-27; config re-chosen every 6 months from past data only.

## Verdict: **FAIL**

| | Strategy | Buy & hold SPY |
|---|---:|---:|
| $1,000 became | $2,130 | $7,913 |
| Yearly return | +5.2% | +15.0% |
| Sharpe | 0.75 | 0.93 |
| Worst drop | -17.1% | -33.7% |
| Deflated Sharpe (267 trials) | 0.509 | |

| Check | Result |
|---|---|
| sharpe>=1 | **no** |
| dsr>=0.95 | **no** |
| beats_tbills | yes |
| max_dd<=25% | yes |
| changes>=30 | yes |
| beats_benchmark_sharpe | **no** |

## Config chosen at each refit

| Refit | Chosen | Training Sharpe |
|---|---|---:|
| 2012-01-01 | sma100-vol8-btc | 0.93 |
| 2012-07-01 | sma100-vol8-btc | 0.83 |
| 2013-01-01 | sma100-vol8-btc | 0.76 |
| 2013-07-01 | sma100-vol8-btc | 0.67 |
| 2014-01-01 | mom252-vol8-btc | 0.74 |
| 2014-07-01 | mom252-vol8-btc | 0.8 |
| 2015-01-01 | mom252-vol8-btc | 0.78 |
| 2015-07-01 | mom252-vol8-btc | 0.71 |
| 2016-01-01 | mom252-vol8-btc | 0.64 |
| 2016-07-01 | mom252-vol8-btc | 0.75 |
| 2017-01-01 | sma100-vol8-btc | 0.74 |
| 2017-07-01 | sma100-vol8-btc | 0.83 |
| 2018-01-01 | mom252-vol8-btc | 0.93 |
| 2018-07-01 | sma100-vol8-btc | 0.84 |
| 2019-01-01 | sma100-vol8-btc | 0.73 |
| 2019-07-01 | sma100-vol8-btc | 0.81 |
| 2020-01-01 | sma100-vol8-btc | 0.83 |
| 2020-07-01 | sma100-vol8-btc | 0.82 |
| 2021-01-01 | sma100-vol8-btc | 0.91 |
| 2021-07-01 | sma100-vol8-btc | 0.97 |
| 2022-01-01 | sma100-vol8-btc | 0.94 |
| 2022-07-01 | sma100-vol8-btc | 0.9 |
| 2023-01-01 | sma100-vol8-btc | 0.83 |
| 2023-07-01 | sma100-vol8-btc | 0.83 |
| 2024-01-01 | sma100-vol8-btc | 0.83 |
| 2024-07-01 | sma100-vol8-btc | 0.84 |
| 2025-01-01 | sma100-vol8-btc | 0.83 |
| 2025-07-01 | sma100-vol8-btc | 0.85 |
| 2026-01-01 | sma100-vol8-btc | 0.88 |
| 2026-07-01 | sma100-vol8-btc | 0.88 |

## By year (out of sample)

| Year | Return |
|---|---:|
| 2012 | -1.3% |
| 2013 | +3.2% |
| 2014 | +6.0% |
| 2015 | -2.7% |
| 2016 | +6.6% |
| 2017 | +19.8% |
| 2018 | -12.6% |
| 2019 | +14.4% |
| 2020 | +14.8% |
| 2021 | +10.4% |
| 2022 | -4.9% |
| 2023 | +6.2% |
| 2024 | +6.9% |
| 2025 | +12.7% |
| 2026 | +3.1% |
