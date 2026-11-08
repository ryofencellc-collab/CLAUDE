# Round 36: beating retail traders' documented mistakes (US stocks)

Rules: [PROTOCOL_ROUND36.md](../PROTOCOL_ROUND36.md). Next-open entry, 0.30% round trip, short borrow (20%/yr hot, 5% other); filters on the real traded price (split history undone) >= $10 and >= $50M a day. Universe 5,112 stocks; dev 2015–2021, holdout 2022–2026. Survivorship bias: delisted stocks missing.

SPY buy-and-hold: dev 14.8%/yr (Sharpe 0.87); holdout 10.9%/yr (Sharpe 0.68, worst drop -24%).
**Sanity check — the average tradable stock, equal-weighted, daily:** dev 13.8%/yr, holdout 7.5%/yr. If this is far from the market's ~10%/yr, the universe is contaminated and the table below should not be trusted.

**0 of 20 pass.**

| test                                               |   dev %/yr |   dev Sharpe |   hold %/yr |   hold Sharpe |   hold t | hold worst drop   |   hold trades | avg trade (net)   |   $25k/day | PASS   |
|:---------------------------------------------------|-----------:|-------------:|------------:|--------------:|---------:|:------------------|--------------:|:------------------|-----------:|:-------|
| 1 frenzy fade, short 20d                           |      -10.6 |        -0.09 |        54.1 |          1.14 |     2.5  | -48%              |           424 | 4.02%             |      37.05 |        |
| 6 gap-up fade intraday >= 20%                      |        9.2 |         1.06 |         7.1 |          0.61 |     1.34 | -19%              |           376 | 0.99%             |       4.87 |        |
| 1 frenzy fade, short 5d                            |        9.6 |         0.48 |         7.2 |          0.38 |     0.85 | -49%              |           591 | 1.60%             |       4.92 |        |
| 2 panic bounce, long 5d                            |       -2.8 |        -0.18 |         4.7 |          0.35 |     0.76 | -25%              |           415 | 0.79%             |       3.2  |        |
| 2 panic bounce, long 20d                           |        4   |         0.29 |         5   |          0.31 |     0.69 | -28%              |           315 | 1.69%             |       3.39 |        |
| 6 gap-up fade intraday >= 10%                      |       -5.9 |        -0.27 |         2.3 |          0.21 |     0.47 | -34%              |          2009 | 0.26%             |       1.56 |        |
| 1 frenzy fade, short 1d                            |       11.2 |         1.09 |        -0.7 |          0.03 |     0.07 | -29%              |           600 | 0.05%             |      -0.45 |        |
| 2 panic bounce, long 1d                            |        0.2 |         0.07 |        -1.1 |         -0.09 |    -0.19 | -30%              |           424 | -0.09%            |      -0.78 |        |
| 7 gap continuation down, short 20d                 |      -26.2 |        -0.83 |        -7.4 |         -0.09 |    -0.21 | -55%              |           598 | -0.31%            |      -5.04 |        |
| 5 52-week high, long near / short far              |       -4.9 |        -0.29 |        -3.9 |         -0.14 |    -0.31 | -40%              |           nan | -                 |      -2.68 |        |
| 10 turn of the month (SPY)                         |        1.1 |         0.19 |        -1.8 |         -0.25 |    -0.55 | -19%              |           nan | -                 |      -1.21 |        |
| 4 MAX lottery, long low / short high               |       -7   |        -0.61 |        -6.8 |         -0.33 |    -0.73 | -52%              |           nan | -                 |      -4.63 |        |
| 3 frenzy chase, long 1d                            |      -14.4 |        -1.44 |        -9.6 |         -0.59 |    -1.29 | -53%              |           600 | -0.73%            |      -6.58 |        |
| 9 penny stocks: short < $5 decile vs long the rest |      -10.7 |        -1.12 |        -8.7 |         -0.69 |    -1.52 | -44%              |           nan | -                 |      -5.95 |        |
| 3 frenzy chase, long 5d                            |      -19.2 |        -0.7  |       -30.1 |         -0.69 |    -1.51 | -85%              |           591 | -2.59%            |     -20.59 |        |
| 8 weekly reversal, long losers / short winners     |      -14.9 |        -1.2  |        -9.9 |         -0.73 |    -1.61 | -50%              |           nan | -                 |      -6.77 |        |
| 7 gap continuation down, short 5d                  |      -18   |        -0.6  |       -25.8 |         -0.78 |    -1.71 | -80%              |          2043 | -0.67%            |     -17.69 |        |
| 4 MAX lottery, short leg only                      |      -35.7 |        -1.38 |       -31.4 |         -0.8  |    -1.77 | -91%              |           nan | -                 |     -21.49 |        |
| 7 gap continuation up, long 20d                    |       -2.4 |         0.08 |       -42.8 |         -0.87 |    -1.92 | -93%              |           596 | -3.62%            |     -29.31 |        |
| 7 gap continuation up, long 5d                     |      -17.7 |        -0.39 |       -42.5 |         -0.95 |    -2.08 | -94%              |          2047 | -1.09%            |     -29.09 |        |
