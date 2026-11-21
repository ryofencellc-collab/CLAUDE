# Round 70: Kalshi S&P 4pm markets vs the SPXW 0DTE option chain

Rules: [PROTOCOL_ROUND70.md](../PROTOCOL_ROUND70.md).

Markets: 1,070 ({'KXINX': 270, 'KXINXU': 800}) over 9 days; market-minutes with a fair value: 107,272.

**Verdict (variant L, live-feasible 15-min-old option data): FAIL.**

## S: same-minute option fair value (upper bound)

Margin chosen on dev: 0.08. Holdout: 91 trades, total $+4.23 per 1-contract set, mean +0.0465, t 1.31, positive days 2/4, Brier option 0.1160 vs Kalshi 0.1188. PASS: False.

|    m |   dev_n |   dev_total |   dev_mean |
|-----:|--------:|------------:|-----------:|
| 0.02 |     195 |       -9.02 |    -0.0463 |
| 0.03 |     159 |       -5.88 |    -0.037  |
| 0.05 |     108 |       -3.94 |    -0.0365 |
| 0.08 |      51 |       -2.26 |    -0.0443 |

Holdout by day:

| day        |   pnl |
|:-----------|------:|
| 2026-11-16 | -0.61 |
| 2026-11-17 |  3.23 |
| 2026-11-18 | -0.17 |
| 2026-11-19 |  1.78 |

Holdout by side:

| side   |   count |   mean |   sum |
|:-------|--------:|-------:|------:|
| no     |      35 |  0.138 |  4.82 |
| yes    |      56 | -0.011 | -0.59 |

## L: 15-minute-old option fair value (what free data allows)

Margin chosen on dev: 0.08. Holdout: 245 trades, total $-42.16 per 1-contract set, mean -0.1721, t -6.43, positive days 1/4, Brier option 0.2533 vs Kalshi 0.1941. PASS: False.

|    m |   dev_n |   dev_total |   dev_mean |
|-----:|--------:|------------:|-----------:|
| 0.02 |     247 |      -22.1  |    -0.0895 |
| 0.03 |     233 |      -18.2  |    -0.0781 |
| 0.05 |     214 |      -15.55 |    -0.0727 |
| 0.08 |     185 |      -10.48 |    -0.0566 |

Holdout by day:

| day        |    pnl |
|:-----------|-------:|
| 2026-11-16 | -12.47 |
| 2026-11-17 |  -6.08 |
| 2026-11-18 |   3.4  |
| 2026-11-19 | -27.01 |

Holdout by side:

| side   |   count |   mean |    sum |
|:-------|--------:|-------:|-------:|
| no     |      72 |  0.115 |   8.31 |
| yes    |     173 | -0.292 | -50.47 |

## Calibration by Kalshi mid band (all market-minutes)

| mid        |   rows |   kalshi_mid |   option_fair |   outcome |
|:-----------|-------:|-------------:|--------------:|----------:|
| (0.0, 0.1] |  29926 |        0.05  |         0.048 |     0.018 |
| (0.1, 0.3] |  23331 |        0.186 |         0.188 |     0.139 |
| (0.3, 0.5] |  12273 |        0.397 |         0.402 |     0.344 |
| (0.5, 0.7] |  11030 |        0.605 |         0.607 |     0.531 |
| (0.7, 0.9] |  18021 |        0.816 |         0.816 |     0.727 |
| (0.9, 1.0] |  12691 |        0.933 |         0.935 |     0.911 |

## |Kalshi mid − option fair| by hour

|   hour |   count |   mean |   median |
|-------:|--------:|-------:|---------:|
|     10 |   26397 |  0.015 |    0.01  |
|     11 |   23037 |  0.014 |    0.01  |
|     12 |   19923 |  0.015 |    0.01  |
|     13 |   16716 |  0.014 |    0.01  |
|     14 |   13571 |  0.016 |    0.011 |
|     15 |    7628 |  0.021 |    0.015 |

