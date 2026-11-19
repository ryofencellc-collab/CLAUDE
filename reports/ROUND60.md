# Round 60: quiet traders on Hyperliquid

Rules: [PROTOCOL_ROUND60.md](../PROTOCOL_ROUND60.md).
Accounts with history: 6000. Data end: 2026-11-19.

## split1 (seen aggregate): select Jun 01 → Sep 01, test Sep 01 → Nov 19

Eligible: 1445; universe mean ROI -13.9%, profitable 28%.

| group                   |   n |   mean_roiB |   median_roiB |      t |   welch_vs_all |   pct_profitable | PASS   |
|:------------------------|----:|------------:|--------------:|-------:|---------------:|-----------------:|:-------|
| Q1 steady earners       |  10 |      -0.124 |         0.015 | -0.89  |          0.106 |             0.6  | False  |
| Q2 low-turnover winners |  50 |      -0.155 |        -0.089 | -4.213 |         -0.4   |             0.24 | False  |
| Q3 small and steady     |  50 |      -0.023 |        -0.049 | -0.318 |          1.582 |             0.4  | False  |

## split2: select Jul 15 → Oct 01, test Oct 01 → Nov 19

Eligible: 1490; universe mean ROI -24.1%, profitable 18%.

| group                   |   n |   mean_roiB |   median_roiB |       t |   welch_vs_all |   pct_profitable | PASS   |
|:------------------------|----:|------------:|--------------:|--------:|---------------:|-----------------:|:-------|
| Q1 steady earners       |  28 |      -0.085 |        -0.02  |  -1.658 |          2.944 |            0.464 | False  |
| Q2 low-turnover winners |  50 |      -0.302 |        -0.295 | -12.623 |         -2.263 |            0.04  | False  |
| Q3 small and steady     |  50 |      -0.184 |        -0.182 |  -3.892 |          1.172 |            0.28  | False  |

## Forward test (the real one)

Selected on Aug 18 → Nov 19 and frozen in `paper/r60_forward_selection.json`: Q1 steady earners: 17, Q2 low-turnover winners: 50, Q3 small and steady: 31 (universe 1294). Scored on Dec 19.

**Split 2 verdict: FAIL.** The overall pass needs split 2 AND the forward test.
