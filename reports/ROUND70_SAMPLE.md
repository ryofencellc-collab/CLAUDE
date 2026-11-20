# Round 70: Kalshi S&P 4pm markets vs the SPXW 0DTE option chain

Rules: [PROTOCOL_ROUND70.md](../PROTOCOL_ROUND70.md).

Markets: 20 ({'KXINX': 10, 'KXINXU': 10}) over 1 days; market-minutes with a fair value: 2,937.

**Verdict (variant L, live-feasible 15-min-old option data): FAIL.**

## S: same-minute option fair value (upper bound)

Margin chosen on dev: 0.08. Holdout: 0 trades, total $+0.00 per 1-contract set, mean +nan, t nan, positive days 0/0, Brier option nan vs Kalshi nan. PASS: False.

|    m |   dev_n |   dev_total |   dev_mean |
|-----:|--------:|------------:|-----------:|
| 0.02 |      13 |       -1.4  |    -0.1077 |
| 0.03 |      10 |       -1.09 |    -0.109  |
| 0.05 |       7 |       -0.64 |    -0.0914 |
| 0.08 |       2 |       -0.37 |    -0.185  |

Holdout by day:

| day   | pnl   |
|-------|-------|

## L: 15-minute-old option fair value (what free data allows)

Margin chosen on dev: 0.03. Holdout: 0 trades, total $+0.00 per 1-contract set, mean +nan, t nan, positive days 0/0, Brier option nan vs Kalshi nan. PASS: False.

|    m |   dev_n |   dev_total |   dev_mean |
|-----:|--------:|------------:|-----------:|
| 0.02 |      15 |       -1.04 |    -0.0693 |
| 0.03 |      15 |       -0.57 |    -0.038  |
| 0.05 |      13 |       -0.87 |    -0.0669 |
| 0.08 |      11 |       -0.75 |    -0.0682 |

Holdout by day:

| day   | pnl   |
|-------|-------|

## Calibration by Kalshi mid band (all market-minutes)

| mid        |   rows |   kalshi_mid |   option_fair |   outcome |
|:-----------|-------:|-------------:|--------------:|----------:|
| (0.0, 0.1] |    438 |        0.057 |         0.048 |         0 |
| (0.1, 0.3] |    363 |        0.191 |         0.187 |         0 |
| (0.3, 0.5] |    108 |        0.365 |         0.36  |         0 |
| (0.5, 0.7] |     58 |        0.66  |         0.681 |         1 |
| (0.7, 0.9] |    996 |        0.836 |         0.841 |         1 |
| (0.9, 1.0] |    974 |        0.932 |         0.935 |         1 |

## |Kalshi mid − option fair| by hour

|   hour |   count |   mean |   median |
|-------:|--------:|-------:|---------:|
|     10 |     652 |  0.013 |    0.01  |
|     11 |     788 |  0.011 |    0.009 |
|     12 |     734 |  0.011 |    0.009 |
|     13 |     562 |  0.012 |    0.01  |
|     14 |     148 |  0.015 |    0.012 |
|     15 |      53 |  0.013 |    0.013 |

