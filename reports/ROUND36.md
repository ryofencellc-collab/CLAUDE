# Round 36: beating retail traders' documented mistakes (US stocks)

Rules: [PROTOCOL_ROUND36.md](../PROTOCOL_ROUND36.md). Next-open entry, 0.20% round trip, short borrow (10%/yr hot, 5% other). Universe 5,111 stocks; dev 2015–2021, holdout 2022–2026. Survivorship bias: delisted stocks missing.

SPY buy-and-hold: dev 14.8%/yr (Sharpe 0.87); holdout 10.9%/yr (Sharpe 0.68, worst drop -24%).

**4 of 20 pass.**

| test                                               |   dev %/yr |   dev Sharpe |   hold %/yr |   hold Sharpe |   hold t | hold worst drop   |    hold trades | avg trade (net)   |   $25k/day | PASS   |
|:---------------------------------------------------|-----------:|-------------:|------------:|--------------:|---------:|:------------------|---------------:|:------------------|-----------:|:-------|
| 7 gap continuation down, short 5d                  |      -23.7 |        -0.46 |       452.2 |          2.71 |     5.95 | -67%              | 2399           | 3.21%             |     309.73 |        |
| 1 frenzy fade, short 20d                           |       44.7 |         0.95 |       430.1 |          2.49 |     5.46 | -60%              |  604           | 14.24%            |     294.61 | YES    |
| 1 frenzy fade, short 5d                            |       51.2 |         0.98 |       338.5 |          2    |     4.39 | -95%              | 2221           | 5.74%             |     231.86 | YES    |
| 7 gap continuation down, short 20d                 |      -15.1 |        -0.29 |       129.9 |          1.65 |     3.62 | -62%              |  610           | 7.80%             |      88.97 |        |
| 1 frenzy fade, short 1d                            |       52.2 |         1.28 |       100.5 |          1.48 |     3.26 | -93%              | 4415           | 1.11%             |      68.85 | YES    |
| 6 gap-up fade intraday >= 20%                      |       72.8 |         2.07 |        87.5 |          1.41 |     3.09 | -74%              |    6.22009e+06 | 1.98%             |      59.9  | YES    |
| 4 MAX lottery, long low / short high               |       -4.8 |        -0.38 |        16.1 |          1.03 |     2.26 | -17%              |  nan           | -                 |      11.03 |        |
| 5 52-week high, long near / short far              |       -5.2 |        -0.3  |        12.8 |          0.78 |     1.71 | -23%              |  nan           | -                 |       8.76 |        |
| 4 MAX lottery, short leg only                      |      -26.6 |        -0.86 |        16.7 |          0.6  |     1.32 | -42%              |  nan           | -                 |      11.42 |        |
| 10 turn of the month (SPY)                         |        2.3 |         0.37 |        -0.6 |         -0.06 |    -0.12 | -17%              |  nan           | -                 |      -0.38 |        |
| 6 gap-up fade intraday >= 10%                      |        6.7 |         0.39 |       -60.6 |         -0.52 |    -1.14 | -100%             |    6.22009e+06 | 1.15%             |     -41.48 |        |
| 8 weekly reversal, long losers / short winners     |       -7.6 |        -0.59 |        -9.3 |         -0.77 |    -1.69 | -46%              |  nan           | -                 |      -6.4  |        |
| 3 frenzy chase, long 1d                            |      -51.6 |        -1.65 |       -80.6 |         -2.07 |    -4.55 | -100%             | 4415           | -1.55%            |     -55.21 |        |
| 3 frenzy chase, long 5d                            |      -62.6 |        -1.19 |       -95.8 |         -2.24 |    -4.92 | -100%             | 2221           | -6.34%            |     -65.58 |        |
| 7 gap continuation up, long 20d                    |      -24   |        -0.38 |       -89.5 |         -2.25 |    -4.95 | -100%             |  609           | -16.68%           |     -61.29 |        |
| 9 penny stocks: short < $5 decile vs long the rest |      -17.6 |        -2.44 |       -24.5 |         -2.31 |    -5.07 | -77%              |  nan           | -                 |     -16.75 |        |
| 7 gap continuation up, long 5d                     |      -65.7 |        -1.33 |       -96.2 |         -2.46 |    -5.4  | -100%             | 2429           | -6.18%            |     -65.92 |        |
| 2 panic bounce, long 5d                            |       -5.9 |        -0.05 |       -87   |         -2.75 |    -6.04 | -100%             | 1395           | -5.28%            |     -59.59 |        |
| 2 panic bounce, long 20d                           |       10.8 |         0.45 |       -85.4 |         -2.8  |    -6.15 | -100%             |  576           | -11.77%           |     -58.51 |        |
| 2 panic bounce, long 1d                            |       -5.9 |        -0.35 |       -61.1 |         -3.02 |    -6.64 | -99%              | 1713           | -2.53%            |     -41.85 |        |
