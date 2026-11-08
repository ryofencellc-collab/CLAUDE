# Round 35: calls and puts on real option prices ($25,000)

Rules: [PROTOCOL_ROUND35.md](../PROTOCOL_ROUND35.md). Natural fills (sell at bid, buy at ask), $0.65/contract/leg. Dev 2020-03-01–2024-01-01, holdout 2024-01-01–2026-12-01, each starting at $25,000.

Benchmark, SPY buy-and-hold on the holdout: 16.8%/yr, Sharpe 1.07, worst drop -19%.

| strategy                                      | dev CAGR   |   dev Sharpe | hold CAGR   |   hold Sharpe | hold worst drop   |   hold trades | hold win %   | $25k ->   |   $/day | PASS                                        |
|:----------------------------------------------|:-----------|-------------:|:------------|--------------:|:------------------|--------------:|:-------------|:----------|--------:|:--------------------------------------------|
| S1 put spread d0.16 no filter                 | 9.4%       |         2.07 | -1.0%       |         -0.15 | -14%              |            81 | 86%          | $24,325   |   -0.65 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S1 put spread d0.16 trend                     | 5.4%       |         2.02 | 4.4%        |          1.02 | -6%               |            93 | 89%          | $28,290   |    3.16 | no (CAGR>=15%, DSR>=0.95)                   |
| S1 put spread d0.16 ivr                       | 0.5%       |         1.5  | -1.6%       |         -0.49 | -11%              |            27 | 78%          | $23,846   |   -1.11 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S1 put spread d0.16 trend+ivr                 | 0.2%       |         0.85 | -0.1%       |         -0.03 | -4%               |            17 | 82%          | $24,940   |   -0.06 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S1 put spread d0.3 no filter                  | -3.0%      |        -0.25 | 2.2%        |          0.26 | -24%              |           141 | 82%          | $26,577   |    1.52 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S1 put spread d0.3 trend                      | 5.2%       |         0.84 | 6.4%        |          0.72 | -13%              |           119 | 84%          | $29,809   |    4.62 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S1 put spread d0.3 ivr                        | 1.4%       |         1.45 | -2.3%       |         -0.36 | -20%              |            31 | 74%          | $23,404   |   -1.53 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S1 put spread d0.3 trend+ivr                  | 0.5%       |         0.81 | 0.3%        |          0.1  | -11%              |            23 | 78%          | $25,219   |    0.21 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S1h put spread d0.16 no filter hold to expiry | 8.4%       |         1.73 | 2.6%        |          0.5  | -14%              |           100 | 90%          | $26,930   |    1.86 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S1h put spread d0.16 trend hold to expiry     | 4.8%       |         1.67 | 6.9%        |          1.51 | -6%               |           103 | 93%          | $30,257   |    5.05 | no (CAGR>=15%, DSR>=0.95)                   |
| S1h put spread d0.3 no filter hold to expiry  | -3.0%      |        -0.23 | 6.1%        |          0.58 | -25%              |           141 | 86%          | $29,611   |    4.43 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S1h put spread d0.3 trend hold to expiry      | 5.7%       |         0.93 | 8.4%        |          0.88 | -14%              |           119 | 87%          | $31,440   |    6.19 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S2 iron condor d0.16 no filter                | 2.0%       |         0.3  | -7.2%       |         -0.94 | -20%              |            66 | 65%          | $20,185   |   -4.63 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95)        |
| S2 iron condor d0.16 ivr                      | -1.2%      |        -0.41 | -6.2%       |         -1.08 | -17%              |            23 | 57%          | $20,849   |   -3.99 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S3 call spread d0.30 downtrend                | -3.4%      |        -0.45 | -6.9%       |         -1.29 | -21%              |            11 | 27%          | $20,392   |   -4.43 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S4 call debit spread on breakouts             | -1.7%      |        -0.13 | 4.7%        |          0.55 | -9%               |            23 | 65%          | $28,493   |    3.36 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S5 put debit spread on breakdowns             | -4.4%      |        -0.91 | -2.0%       |         -0.63 | -6%               |             3 | 33%          | $23,595   |   -1.35 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S6a earnings iron fly                         | -2.0%      |        -0.37 | 0.7%        |          0.14 | -12%              |            24 | 46%          | $25,494   |    0.48 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S6b earnings 16d iron condor                  | -7.1%      |        -1.76 | 0.0%        |          0.03 | -4%               |            35 | 74%          | $25,035   |    0.03 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S6c earnings long straddle                    | -1.8%      |        -1.34 | 0.0%        |          0    | 0%                |             0 | -            | $25,000   |    0    | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |
| S7 put spread d0.30 VIX contango              | -1.4%      |        -0.11 | 6.5%        |          0.73 | -13%              |           119 | 84%          | $29,871   |    4.68 | no (Sharpe>=1, CAGR>=15%, DSR>=0.95, dev>0) |

## Combo (dev-best of each family that made money on dev, one account, risk split equally)

Members: S1 put spread d0.16 no filter, S1h put spread d0.16 no filter hold to expiry, S2 iron condor d0.16 no filter

Dev: 17.0%/yr, Sharpe 1.66. **Holdout: 4.2%/yr, Sharpe 0.48, worst drop -18%, $25k → $28,089 ($2.97/day), deflated Sharpe 0.01.**

By member (holdout):

| strategy                                      |   count |     sum |   mean |
|:----------------------------------------------|--------:|--------:|-------:|
| S1 put spread d0.16 no filter                 |      51 |  846.1  |  16.59 |
| S1h put spread d0.16 no filter hold to expiry |      50 |  993    |  19.86 |
| S2 iron condor d0.16 no filter                |      57 | 1282.79 |  22.51 |

Worst holdout trades, S1 put spread d0.16 no filter: SPY 2024-07-08 expiry $-991; SPY 2025-02-17 expiry $-933; SPY 2025-03-10 expiry $-889
Worst holdout trades, S1 put spread d0.16 trend: SPY 2024-07-08 expiry $-991; SPY 2025-02-24 expiry $-777; SPY 2024-07-15 expiry $-552
Worst holdout trades, S1 put spread d0.16 ivr: SPY 2025-03-10 expiry $-889; SPY 2025-02-24 expiry $-777; SPY 2025-03-17 expiry $-550
Worst holdout trades, S1 put spread d0.16 trend+ivr: SPY 2025-02-24 expiry $-777; SPY 2025-02-10 expiry $-336; SPY 2026-03-16 21 days left $-64
Worst holdout trades, S1 put spread d0.3 no filter: SPY 2025-03-10 expiry $-1,232; SPY 2026-02-09 expiry $-1,177; SPY 2025-10-27 expiry $-1,173
Worst holdout trades, S1 put spread d0.3 trend: SPY 2026-02-09 expiry $-1,177; SPY 2025-10-27 expiry $-1,173; SPY 2026-02-02 expiry $-1,143
Worst holdout trades, S1 put spread d0.3 ivr: SPY 2025-03-10 expiry $-1,232; SPY 2025-02-10 expiry $-1,116; SPY 2025-02-24 expiry $-987
Worst holdout trades, S1 put spread d0.3 trend+ivr: SPY 2025-02-10 expiry $-1,116; SPY 2025-02-24 expiry $-987; SPY 2025-03-03 expiry $-948
Worst holdout trades, S1h put spread d0.16 no filter hold to expiry: SPY 2024-07-08 expiry $-991; SPY 2025-02-17 expiry $-933; SPY 2025-03-10 expiry $-889
Worst holdout trades, S1h put spread d0.16 trend hold to expiry: SPY 2024-07-08 expiry $-991; SPY 2025-02-24 expiry $-777; SPY 2024-07-15 expiry $-552
Worst holdout trades, S1h put spread d0.3 no filter hold to expiry: SPY 2025-03-10 expiry $-1,232; SPY 2026-02-09 expiry $-1,177; SPY 2025-10-27 expiry $-1,173
Worst holdout trades, S1h put spread d0.3 trend hold to expiry: SPY 2026-02-09 expiry $-1,177; SPY 2025-10-27 expiry $-1,173; SPY 2026-02-02 expiry $-1,143
Worst holdout trades, S2 iron condor d0.16 no filter: SPY 2026-03-30 expiry $-1,002; SPY 2026-04-20 expiry $-975; SPY 2025-04-07 expiry $-955
Worst holdout trades, S2 iron condor d0.16 ivr: SPY 2026-03-30 expiry $-1,002; SPY 2025-04-07 expiry $-955; SPY 2025-03-10 expiry $-771
Worst holdout trades, S3 call spread d0.30 downtrend: SPY 2026-04-06 expiry $-1,120; SPY 2026-03-23 expiry $-932; SPY 2026-03-30 expiry $-832
Worst holdout trades, S4 call debit spread on breakouts: SPY 2025-10-27 expiry $-1,405; SPY 2025-09-22 expiry $-1,261; SPY 2026-06-01 expiry $-1,150
Worst holdout trades, S5 put debit spread on breakdowns: SPY 2026-03-30 expiry $-1,169; SPY 2025-04-07 debit exit $-659; SPY 2025-03-10 expiry $423
Worst holdout trades, S6a earnings iron fly: TSLA 2025-04-21 expiry $-665; AMZN 2025-04-30 expiry $-659; TSLA 2024-01-22 expiry $-648
Worst holdout trades, S6b earnings 16d iron condor: AAPL 2026-04-29 expiry $-417; AAPL 2025-07-30 expiry $-414; TSLA 2024-04-22 expiry $-409
Worst holdout trades, S7 put spread d0.30 VIX contango: SPY 2026-02-09 expiry $-1,177; SPY 2025-10-27 expiry $-1,173; SPY 2026-02-02 expiry $-1,143
