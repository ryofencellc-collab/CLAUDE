# Round 59: do Hyperliquid's winning traders keep winning?

Rules: [PROTOCOL_ROUND59.md](../PROTOCOL_ROUND59.md).

Leaderboard accounts: 48003; volume ≥ $5M: 40436; sampled with history: 5999; eligible: 1399. Selection window Jun 1 → Sep 1 2026, test window Sep 1 → now.

Eligible universe in the test window: mean ROI -12.0%, profitable 30%.

**Verdict: FAIL.**

## Groups picked on the selection window, scored on the test window

| group                       |   n |   mean_roiB |   median_roiB |      t |   welch_vs_all |   pct_profitable |   pnlB_total | PASS   |
|:----------------------------|----:|------------:|--------------:|-------:|---------------:|-----------------:|-------------:|:-------|
| G1 top PnL_A                |  50 |      -0.152 |        -0.106 | -3.454 |         -0.698 |             0.24 |  4.97577e+06 | False  |
| G2 top ROI_A (PnL_A ≥ $10k) |  50 |      -0.282 |        -0.511 | -2.766 |         -1.575 |             0.36 | -1.26486e+07 | False  |
| G3 steadiest (PnL_A > 0)    |  50 |      -0.148 |        -0.14  | -2.531 |         -0.466 |             0.32 | -9.11373e+06 | False  |

## Persistence by ROI decile (decile 10 = best in the selection window)

|   decA |   n |   mean_roiA |   mean_roiB |   pct_profitable_B |
|-------:|----:|------------:|------------:|-------------------:|
|      1 | 140 |      -1.518 |      -0.132 |              0.321 |
|      2 | 140 |      -0.21  |      -0.021 |              0.386 |
|      3 | 140 |      -0.017 |      -0.053 |              0.329 |
|      4 | 140 |       0.042 |      -0.095 |              0.314 |
|      5 | 140 |       0.127 |      -0.131 |              0.321 |
|      6 | 139 |       0.207 |      -0.1   |              0.288 |
|      7 | 140 |       0.268 |      -0.097 |              0.257 |
|      8 | 140 |       0.336 |      -0.184 |              0.236 |
|      9 | 140 |       0.47  |      -0.128 |              0.271 |
|     10 | 140 |       1.178 |      -0.259 |              0.321 |
