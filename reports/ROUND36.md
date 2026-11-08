# Round 36: beating retail traders' documented mistakes (US stocks)

Rules: [PROTOCOL_ROUND36.md](../PROTOCOL_ROUND36.md). Next-open entry, 0.20% round trip, short borrow (10%/yr hot, 5% other). Universe 5,112 stocks; dev 2015–2021, holdout 2022–2026. Survivorship bias: delisted stocks missing.

SPY buy-and-hold: dev 14.8%/yr (Sharpe 0.87); holdout 10.9%/yr (Sharpe 0.68, worst drop -24%).

**2 of 20 pass.**

| test                                               |   dev %/yr |   dev Sharpe |   hold %/yr |   hold Sharpe |   hold t | hold worst drop   |   hold trades | avg trade (net)   |   $25k/day | PASS   |
|:---------------------------------------------------|-----------:|-------------:|------------:|--------------:|---------:|:------------------|--------------:|:------------------|-----------:|:-------|
| 1 frenzy fade, short 20d                           |       16.8 |         0.59 |       256.2 |          2.44 |     5.35 | -44%              |           481 | 12.76%            |     175.48 | YES    |
| 1 frenzy fade, short 5d                            |       11.9 |         0.5  |        95.5 |          1.52 |     3.33 | -45%              |           735 | 5.49%             |      65.41 | YES    |
| 7 gap continuation down, short 20d                 |      -21.4 |        -0.57 |        35   |          1.03 |     2.26 | -31%              |           602 | 1.86%             |      24    |        |
| 6 gap-up fade intraday >= 20%                      |       15.1 |         1.15 |        16.9 |          0.89 |     1.95 | -18%              |           467 | 1.82%             |      11.56 |        |
| 1 frenzy fade, short 1d                            |       25.1 |         1.31 |        19.2 |          0.86 |     1.89 | -32%              |           748 | 1.32%             |      13.14 |        |
| 6 gap-up fade intraday >= 10%                      |       -0   |         0.11 |        19.3 |          0.75 |     1.65 | -28%              |          2217 | 0.62%             |      13.19 |        |
| 7 gap continuation down, short 5d                  |      -14.9 |        -0.39 |        15.6 |          0.57 |     1.26 | -58%              |          2077 | 0.36%             |      10.66 |        |
| 4 MAX lottery, long low / short high               |       -5.1 |        -0.38 |         0.4 |          0.11 |     0.23 | -36%              |           nan | -                 |       0.26 |        |
| 5 52-week high, long near / short far              |       -3   |        -0.13 |        -0   |          0.09 |     0.19 | -30%              |           nan | -                 |      -0.01 |        |
| 10 turn of the month (SPY)                         |        1.1 |         0.19 |        -1.8 |         -0.25 |    -0.55 | -19%              |           nan | -                 |      -1.21 |        |
| 4 MAX lottery, short leg only                      |      -33   |        -1.15 |       -20.2 |         -0.4  |    -0.88 | -84%              |           nan | -                 |     -13.85 |        |
| 8 weekly reversal, long losers / short winners     |      -15.7 |        -1.23 |        -8.8 |         -0.64 |    -1.4  | -48%              |           nan | -                 |      -6.02 |        |
| 2 panic bounce, long 20d                           |        2.6 |         0.23 |       -29.1 |         -0.87 |    -1.92 | -82%              |           335 | -2.25%            |     -19.93 |        |
| 2 panic bounce, long 1d                            |        1.3 |         0.19 |       -11.9 |         -1.03 |    -2.26 | -57%              |           461 | -1.26%            |      -8.16 |        |
| 2 panic bounce, long 5d                            |       -2.7 |        -0.1  |       -26.6 |         -1.15 |    -2.52 | -84%              |           451 | -2.05%            |     -18.21 |        |
| 3 frenzy chase, long 1d                            |      -27.1 |        -1.6  |       -28.7 |         -1.3  |    -2.86 | -84%              |           748 | -2.00%            |     -19.64 |        |
| 3 frenzy chase, long 5d                            |      -32.3 |        -0.67 |       -67.5 |         -1.79 |    -3.94 | -100%             |           735 | -6.48%            |     -46.25 |        |
| 7 gap continuation up, long 5d                     |      -33.5 |        -0.6  |       -77.5 |         -2    |    -4.39 | -100%             |          2116 | -2.96%            |     -53.1  |        |
| 7 gap continuation up, long 20d                    |      -21.2 |        -0.4  |       -75.3 |         -2.16 |    -4.74 | -100%             |           596 | -8.88%            |     -51.59 |        |
| 9 penny stocks: short < $5 decile vs long the rest |      -18.5 |        -2.58 |       -24.6 |         -2.31 |    -5.08 | -77%              |           nan | -                 |     -16.83 |        |
