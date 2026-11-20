# Round 66: 0DTE search, 14 years of S&P minutes, option prices calibrated to real 0DTE quotes

Rules: [PROTOCOL_ROUND66.md](../PROTOCOL_ROUND66.md).

Days: SPX 2,151 (2014-04-11 → 2026-10-30), NDX 3,443. Dev < 2020, holdout ≥ 2020.
Search: **3,581 signals × 6 option types × 100 exits = 2,148,600 configurations** (dev only).

**Verdict: PASS → real-quote check next.** (Top 20 dev configurations tested once on the holdout; pass needs all five criteria.)

## Top 20 dev configurations on the holdout

Excess = P&L minus the same option/exit bought unconditionally at the same slot (cancels pricing-model level bias).

| rule                                                 | type       | exit               |   dev_n |   dev_t |   ho_n |   ho_mean |   ho_excess |   ho_t |   ho_h1 |   ho_h2 |   ndx_excess |   dsr | PASS   |
|:-----------------------------------------------------|:-----------|:-------------------|--------:|--------:|-------:|----------:|------------:|-------:|--------:|--------:|-------------:|------:|:-------|
| rv30 >= 0.1596 (p80) AND ret30 <= -8.979 (p30)       | call OTM30 | (0.25, None, None) |     279 |    6.67 |    650 |     54.04 |      114.79 |   8.06 |   80.37 |  178.5  |       175.3  | 1     | True   |
| rv30 >= 0.1596 (p80) AND vs_low <= 15.94 (p30)       | call OTM30 | (0.25, None, None) |     239 |    6.6  |    529 |     42.28 |      102.58 |   6.27 |   70.16 |  160.9  |       145.03 | 1     | True   |
| rv30 >= 0.1596 (p80) AND ema9_21 <= -1.723 (p30)     | call OTM30 | (0.25, None, None) |     276 |    6.48 |    647 |     44.9  |      105.3  |   7.13 |   77.95 |  156.93 |       155.88 | 1     | True   |
| macd_slope <= -0.5211 (p30) AND rv30 >= 0.1596 (p80) | call ATM   | (0.5, None, None)  |     274 |    6.39 |    665 |    171.05 |      259.9  |   6.34 |  228.75 |  318.81 |       363.52 | 1     | True   |
| rv30 >= 0.1353 (p70) AND ema9_21 <= -1.723 (p30)     | call OTM30 | (0.25, None, None) |     356 |    6.14 |    836 |     28.98 |       89.04 |   7    |   68.5  |  122    |       120.73 | 1     | True   |
| macd_slope <= -0.5211 (p30) AND rv30 >= 0.1596 (p80) | call OTM30 | (0.25, None, None) |     274 |    6.09 |    665 |     45.07 |      103.98 |   7    |   87.08 |  135.94 |       144.51 | 1     | True   |
| macd_slope <= -0.5211 (p30) AND rv30 >= 0.1596 (p80) | call ATM   | (0.25, None, None) |     274 |    6.06 |    665 |     78.32 |      159.63 |   5.19 |  146.09 |  185.24 |       206.21 | 0.995 | True   |
| ret15 <= -18.41 (p10) AND ret30 <= -26.78 (p10)      | put OTM30  | (0.5, None, None)  |     320 |    6.04 |    755 |     -6.66 |      108.95 |   5.71 |   95.79 |  128.48 |       291.24 | 0.999 | False  |
| ret30 <= -26.78 (p10) AND ret15 <= -18.41 (p10)      | put OTM30  | (0.5, None, None)  |     320 |    6.04 |    755 |     -6.66 |      108.95 |   5.71 |   95.79 |  128.48 |       291.24 | 0.999 | False  |
| rv30 >= 0.1596 (p80)                                 | call OTM30 | (0.25, None, None) |     351 |    5.94 |    798 |     33.19 |       93.13 |   6.67 |   83.23 |  109.56 |       102.26 | 1     | True   |
| vs_mean <= -22.71 (p20) AND ret15 <= -18.41 (p10)    | put OTM30  | (0.5, None, None)  |     310 |    5.91 |    727 |     -7.54 |      109.55 |   5.72 |   95.64 |  129.03 |       362.85 | 0.999 | False  |
| rv30 >= 0.1596 (p80) AND vs_low <= 15.94 (p30)       | call OTM30 | (0.5, None, None)  |     239 |    5.9  |    529 |     54.9  |      132.49 |   6.02 |   93.63 |  202.4  |       254.14 | 1     | True   |
| rv30 >= 0.1596 (p80) AND rsi <= 43.63 (p30)          | call OTM30 | (0.25, None, None) |     251 |    5.88 |    575 |     56.61 |      117.21 |   7.5  |   81.41 |  187.52 |       191.16 | 1     | True   |
| rv30 >= 0.1997 (p90)                                 | call ATM   | (0.5, None, None)  |     210 |    5.87 |    547 |    216.93 |      295.78 |   6.4  |  251.06 |  397.54 |       377.71 | 1     | True   |
| rv30 >= 0.1353 (p70) AND ret30 <= -8.979 (p30)       | call OTM30 | (0.25, None, None) |     362 |    5.84 |    830 |     37.4  |       98.14 |   7.85 |   74.02 |  136.39 |       135.01 | 1     | True   |
| ret15 <= -18.41 (p10) AND ret30 <= -26.78 (p10)      | put OTM30  | (0.5, -0.75, 120)  |     320 |    5.83 |    755 |     -8.45 |       72.61 |   4.54 |   64.68 |   84.38 |       237.94 | 0.983 | False  |
| ret30 <= -26.78 (p10) AND ret15 <= -18.41 (p10)      | put OTM30  | (0.5, -0.75, 120)  |     320 |    5.83 |    755 |     -8.45 |       72.61 |   4.54 |   64.68 |   84.38 |       237.94 | 0.983 | False  |
| macd_slope <= -0.5211 (p30) AND rv30 >= 0.1596 (p80) | call OTM30 | (0.5, None, None)  |     274 |    5.82 |    665 |     70.28 |      147.14 |   7.07 |  117.68 |  202.86 |       179.92 | 1     | True   |
| rv30 >= 0.1596 (p80)                                 | call OTM30 | (0.5, None, None)  |     351 |    5.82 |    798 |     33.7  |      108.02 |   5.62 |   88.26 |  140.82 |       153.71 | 0.999 | True   |
| rv30 >= 0.1596 (p80) AND vs_open <= -26.61 (p30)     | call OTM30 | (0.5, None, None)  |     209 |    5.79 |    471 |     83.41 |      160.49 |   7.09 |  136.17 |  206.87 |       244.74 | 1     | True   |

## How the best dev configurations did on the holdout (distribution)

Top 500 dev configurations: holdout excess > 0 in 500/500; holdout t ≥ 2 in 497; t ≥ 3 in 478. Median holdout t 4.93 (dev median t 4.91).

## Context: unconditional option buying at 10:00 (model prices; level not trusted, see protocol)

| type       | exit                |   dev_mean |   ho_mean |
|:-----------|:--------------------|-----------:|----------:|
| put ATM    | (None, None, None)  |     133.02 |   -112.13 |
| put ATM    | (2.0, None, None)   |     123.63 |   -151.33 |
| put OTM30  | (None, None, None)  |     117.47 |    -69.38 |
| put ITM70  | (None, None, None)  |     116.52 |   -163.23 |
| put ITM70  | (2.0, None, None)   |     100.62 |   -160.36 |
| put ITM70  | (1.0, None, None)   |      87.86 |   -204.72 |
| put ATM    | (2.0, -0.75, None)  |      87.76 |   -131.4  |
| call ATM   | (None, None, None)  |      81.16 |      7.46 |
| put OTM30  | (None, -0.75, None) |      76    |    -81.87 |
| call OTM30 | (None, None, None)  |      72.61 |    -33.31 |

| type       | exit               |   dev_mean |   ho_mean |
|:-----------|:-------------------|-----------:|----------:|
| call ITM70 | (1.0, -0.5, None)  |     -62.06 |    -77.13 |
| call ITM70 | (2.0, -0.5, 60)    |     -62.51 |      7.57 |
| call ITM70 | (1.0, -0.25, 120)  |     -62.76 |    -52.39 |
| call ITM70 | (1.0, -0.25, None) |     -75.65 |    -85.55 |
| call ITM70 | (1.0, -0.75, None) |     -79.25 |    -79.77 |
