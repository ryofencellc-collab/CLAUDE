# Round 37: beating retail crypto traders (all Binance USDT pairs)

Rules: [PROTOCOL_ROUND37.md](../PROTOCOL_ROUND37.md). Crypto trades 365 days a year; annualisation uses 252 steps for comparability with stocks, so Sharpe/annual figures are slightly understated.
(Copied from the run log of run 42515564765: the workflow saved the wrong report name; fixed for later runs.)

Pairs: 685. **1 of 13 pass.**

| test                                           |   dev %/yr |   dev Sharpe |   hold %/yr |   hold Sharpe |   hold t | hold worst drop   |   hold trades | avg trade (net)   | PASS   |
|:-----------------------------------------------|-----------:|-------------:|------------:|--------------:|---------:|:------------------|--------------:|:------------------|:-------|
| 1 pump fade >= 30%, short 3d                   |        9.9 |         0.49 |        78.4 |          1.31 |     3.08 | -41%              |          1051 | 4.79%             | YES    |
| 1 pump fade >= 20%, short 1d                   |       13.4 |         0.55 |        54.6 |          1.23 |     2.89 | -35%              |          1964 | 1.51%             |        |
| 1 pump fade >= 30%, short 1d                   |        9.1 |         0.46 |        44.8 |          1.21 |     2.85 | -28%              |          1082 | 2.25%             |        |
| 1 pump fade >= 20%, short 3d                   |        2.4 |         0.43 |        71.1 |          1.14 |     2.68 | -55%              |          1767 | 2.92%             |        |
| 1 pump fade >= 30%, short 7d                   |      -25.7 |         0.05 |        66.2 |          1.09 |     2.58 | -77%              |           897 | 6.25%             |        |
| 1 pump fade >= 20%, short 7d                   |      -20.1 |         0.2  |        53.9 |          1    |     2.36 | -76%              |          1287 | 4.60%             |        |
| 3 new-listing fade, short days 4-30            |      -18.9 |        -0.02 |        38   |          0.9  |     2.11 | -55%              |           258 | 9.44%             |        |
| 6 BTC weekend (Fri close -> Sun close)         |       -6.5 |        -0.17 |         0.8 |          0.12 |     0.29 | -34%              |           nan | -                 |        |
| 5 momentum 30d, long winners / short losers    |      -15.2 |        -0.57 |        -9.7 |         -0.28 |    -0.66 | -64%              |           nan | -                 |        |
| 4 weekly reversal, long losers / short winners |       -7   |        -0.16 |       -13.8 |         -0.49 |    -1.16 | -77%              |           nan | -                 |        |
| 2 dump bounce, long 3d                         |      -19.1 |        -0.79 |       -26.1 |         -0.94 |    -2.22 | -82%              |           263 | -6.12%            |        |
| 2 dump bounce, long 1d                         |      -10.1 |        -0.77 |       -14.9 |         -1.09 |    -2.58 | -60%              |           264 | -3.19%            |        |
| 2 dump bounce, long 7d                         |      -21.4 |        -0.64 |       -47.4 |         -1.58 |    -3.73 | -97%              |           254 | -11.41%           |        |
