# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.94 (official close), 27 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.69 (official close), 27 trades
- 2026-11-10 SPXW: 419 snapshots, settle 7520.93 (official close), 27 trades
- 2026-11-10 SPY: 412 snapshots, settle 749.92 (official close), 27 trades
- 2026-11-11 SPXW: 424 snapshots, settle 7619.38 (official close), 26 trades
- 2026-11-11 SPY: 424 snapshots, settle 759.81 (official close), 26 trades
- 2026-11-12 SPXW: 424 snapshots, settle 7592.40 (official close), 27 trades
- 2026-11-12 SPY: 424 snapshots, settle 757.12 (official close), 27 trades
- 2026-11-13 SPXW: 423 snapshots, settle 7561.67 (official close), 27 trades
- 2026-11-13 SPY: 423 snapshots, settle 754.37 (official close), 27 trades
- 2026-11-16 SPXW: 423 snapshots, settle 7416.59 (official close), 27 trades
- 2026-11-16 SPY: 423 snapshots, settle 739.95 (official close), 27 trades
- 2026-11-17 SPXW: 420 snapshots, settle 7340.53 (official close), 27 trades
- 2026-11-17 SPY: 413 snapshots, settle 732.44 (official close), 27 trades

Trading days scored: **7** (verdict at 20).

| strategy                                  | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |      h1 |       h2 |
|:------------------------------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|--------:|---------:|
| B1 OR breakout                            | SPXW   | -       |        7 | 57%   |  485.57 |  -422.07 | -1273    |  3399    | 1891    |  1508    |
| B1 OR breakout                            | SPY    | -       |        7 | 71%   |  110.56 |     7.84 |  -146.3  |   773.9  |  233.1  |   540.8  |
| B2 breakout by 11:00 only                 | SPXW   | -       |        7 | 57%   |  485.57 |  -422.07 | -1273    |  3399    | 1891    |  1508    |
| B2 breakout by 11:00 only                 | SPY    | -       |        7 | 71%   |  110.56 |     7.84 |  -146.3  |   773.9  |  233.1  |   540.8  |
| B3 breakout with the day (vs prior close) | SPXW   | -       |        7 | 71%   |  954.14 |    88.43 | -1273    |  6679    | 1981    |  4698    |
| B3 breakout with the day (vs prior close) | SPY    | -       |        7 | 71%   |  146.99 |    36.56 |  -102.3  |  1028.9  |  249.1  |   779.8  |
| B4 breakout on high-VIX1D days            | SPXW   | -       |        6 | 50%   |  407    |  -674.67 | -1273    |  2442    | 2601    |  -159    |
| B4 breakout on high-VIX1D days            | SPY    | -       |        6 | 67%   |  107.37 |   -13.48 |  -146.3  |   644.2  |  281.1  |   363.1  |
| B5 breakout, -50% stop, no target         | SPXW   | -       |        7 | 29%   |  -21.57 | -1061.57 | -1273    |  -151    | 4101    | -4252    |
| B5 breakout, -50% stop, no target         | SPY    | -       |        7 | 43%   |   70.13 |   -71.88 |  -146.3  |   490.9  |  400.1  |    90.8  |
| F1 Reddit iron fly 14:50 (bid/ask fills)  | SPXW   | 14:50   |        7 | 100%  |  150.14 |   136.57 |   123    |  1051    |  414    |   637    |
| F1 Reddit iron fly 14:50 (bid/ask fills)  | SPY    | 14:50   |        7 | 86%   |    6.31 |    -8.94 |   -40.6  |    44.2  |   37.4  |     6.8  |
| F1m same, mid fills                       | SPXW   | 14:50   |        7 | 100%  |  167.29 |   149.43 |   123    |  1171    |  466.5  |   704.5  |
| F1m same, mid fills                       | SPY    | 14:50   |        7 | 86%   |    7.24 |    -7.3  |   -38.1  |    50.7  |   40.4  |    10.3  |
| I1 condor 10d                             | SPXW   | 10:00   |        7 | 100%  |  240.43 |   225.43 |   204    |  1683    |  667    |  1016    |
| I1 condor 10d                             | SPXW   | 11:30   |        7 | 86%   |   12.43 |  -350.76 | -1097.02 |    86.98 |  522    |  -435.02 |
| I1 condor 10d                             | SPXW   | 13:00   |        7 | 86%   |  132.57 |    54.71 |  -116.01 |   927.99 |  397    |   530.99 |
| I1 condor 10d                             | SPXW   | 14:30   |        7 | 100%  |  136.86 |   116.86 |   104    |   958    |  327    |   631    |
| I1 condor 10d                             | SPY    | 10:00   |        7 | 100%  |   26.83 |    23.83 |    20.4  |   187.8  |   79.2  |   108.6  |
| I1 condor 10d                             | SPY    | 11:30   |        7 | 86%   |    5.4  |   -21.46 |   -78.6  |    37.8  |   46.2  |    -8.4  |
| I1 condor 10d                             | SPY    | 13:00   |        7 | 100%  |   17.26 |    13.54 |     8.4  |   120.8  |   36.2  |    84.6  |
| I1 condor 10d                             | SPY    | 14:30   |        7 | 100%  |   11.83 |     8.69 |     5.4  |    82.8  |   20.2  |    62.6  |
| I2 condor 10d stop 2x                     | SPXW   | 10:00   |        7 | 29%   | -150.29 |  -308.43 |  -367    | -1052    | -415    |  -637    |
| I2 condor 10d stop 2x                     | SPXW   | 11:30   |        7 | 57%   |   25    |  -118.86 |  -302    |   175    | -185    |   360    |
| I2 condor 10d stop 2x                     | SPXW   | 13:00   |        7 | 29%   |  -87.43 |  -211.29 |  -302    |  -612    | -531    |   -81    |
| I2 condor 10d stop 2x                     | SPXW   | 14:30   |        7 | 57%   |  -32.14 |  -153.18 |  -377    |  -225    |  101    |  -326    |
| I2 condor 10d stop 2x                     | SPY    | 10:00   |        7 | 29%   |  -21.03 |   -42.49 |   -58.2  |  -147.2  |  -57    |   -90.2  |
| I2 condor 10d stop 2x                     | SPY    | 11:30   |        7 | 57%   |    1.14 |   -15.03 |   -37.2  |     8    |  -25    |    33    |
| I2 condor 10d stop 2x                     | SPY    | 13:00   |        7 | 57%   |   -3.57 |   -20.75 |   -46.2  |   -25    |    7.6  |   -32.6  |
| I2 condor 10d stop 2x                     | SPY    | 14:30   |        7 | 71%   |   -0.77 |   -14.66 |   -40.2  |    -5.4  |  -26.4  |    21    |
| I3 condor 20d                             | SPXW   | 10:00   |        7 | 71%   |  -17.43 |  -565.27 | -1848.02 |  -122.02 |  215.02 |  -337.04 |
| I3 condor 20d                             | SPXW   | 11:30   |        7 | 57%   | -186.86 |  -797.43 | -1926    | -1307.99 |  833.01 | -2141    |
| I3 condor 20d                             | SPXW   | 13:00   |        7 | 71%   |    3.71 |  -445.29 | -1326.01 |    25.97 |  -53.03 |    79    |
| I3 condor 20d                             | SPXW   | 14:30   |        7 | 100%  |  356.86 |   301.14 |   219    |  2498    |  812    |  1686    |
| I3 condor 20d                             | SPY    | 10:00   |        7 | 57%   |   21.54 |   -13.03 |   -84.6  |   150.8  |   42.2  |   108.6  |
| I3 condor 20d                             | SPY    | 11:30   |        7 | 57%   |  -27.17 |   -96.34 |  -233.6  |  -190.2  |   80.2  |  -270.4  |
| I3 condor 20d                             | SPY    | 13:00   |        7 | 71%   |   13.54 |   -12.89 |   -48.6  |    94.8  |   11.2  |    83.6  |
| I3 condor 20d                             | SPY    | 14:30   |        7 | 100%  |   38.83 |    30.83 |    17.4  |   271.8  |   82.2  |   189.6  |
| L1 long straddle                          | SPXW   | 10:00   |        7 | 57%   |  -18.57 | -1517.43 | -2956    |  -129.98 |  822    |  -951.98 |
| L1 long straddle                          | SPXW   | 11:30   |        7 | 43%   |  214.15 | -1171.71 | -3216    |  1499.03 |  387    |  1112.03 |
| L1 long straddle                          | SPXW   | 13:00   |        7 | 43%   |  -80.28 |  -854.57 | -2206    |  -561.99 |   82    |  -643.99 |
| L1 long straddle                          | SPXW   | 14:30   |        7 | 14%   | -351.71 |  -758.14 | -1146    | -2462    |  102    | -2564    |
| L1 long straddle                          | SPY    | 10:00   |        7 | 57%   |   18.26 |  -128.6  |  -274.6  |   127.8  |  158.2  |   -30.4  |
| L1 long straddle                          | SPY    | 11:30   |        7 | 43%   |   48.83 |   -92.17 |  -230.6  |   341.8  |   16.2  |   325.6  |
| L1 long straddle                          | SPY    | 13:00   |        7 | 43%   |  -10.74 |   -72.89 |  -148.6  |   -75.2  |  -33.8  |   -41.4  |
| L1 long straddle                          | SPY    | 14:30   |        7 | 29%   |  -31.31 |   -68.04 |   -91.6  |  -219.2  |  -41.8  |  -177.4  |
| T1 trend spread 15d                       | SPXW   | 10:00   |        7 | 86%   |    1.71 |  -396.04 | -1215.02 |    11.98 |  561    |  -549.02 |
| T1 trend spread 15d                       | SPXW   | 11:30   |        7 | 86%   |   74.86 |  -144.43 |  -608.01 |   523.99 |  461    |    62.99 |
| T1 trend spread 15d                       | SPXW   | 13:00   |        7 | 71%   | -107    |  -413.75 | -1118.01 |  -749.03 | -172.02 |  -577.01 |
| T1 trend spread 15d                       | SPXW   | 14:30   |        7 | 100%  |  118.43 |    98.43 |    72    |   829    |  261    |   568    |
| T1 trend spread 15d                       | SPY    | 10:00   |        7 | 100%  |   23.7  |    22.41 |    21.7  |   165.9  |   68.1  |    97.8  |
| T1 trend spread 15d                       | SPY    | 11:30   |        7 | 86%   |    6.41 |   -17.73 |   -68.3  |    44.9  |   43.1  |     1.8  |
| T1 trend spread 15d                       | SPY    | 13:00   |        7 | 86%   |    3.7  |   -20.44 |   -71.3  |    25.9  |   36.1  |   -10.2  |
| T1 trend spread 15d                       | SPY    | 14:30   |        7 | 100%  |   12.27 |     9.27 |     4.7  |    85.9  |   24.1  |    61.8  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   B2 breakout by 11:00 only |   B3 breakout with the day (vs prior close) |   B4 breakout on high-VIX1D days |   B5 breakout, -50% stop, no target |   F1 Reddit iron fly 14:50 (bid/ask fills) |   F1m same, mid fills |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------------------:|--------------------------------------------:|---------------------------------:|------------------------------------:|-------------------------------------------:|----------------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2259 |                        2259 |                                        2259 |                             2259 |                                4496 |                                        170 |                   214 |             686 |                   -1038 |             186 |               6242 |                   592 |
| 2026-11-10 |            -1221 |                       -1221 |                                       -1115 |                            -1221 |                               -1221 |                                        147 |                   160 |             807 |                     386 |             888 |              -3948 |                   162 |
| 2026-11-11 |             1087 |                        1087 |                                        1087 |                              nan |                                1227 |                                        135 |                   133 |             603 |                    -479 |             950 |               -801 |                   529 |
| 2026-11-12 |             1845 |                        1845 |                                        1355 |                             1845 |                                -833 |                                        155 |                   166 |             494 |                    -230 |           -1734 |               1271 |                 -1490 |
| 2026-11-13 |             2514 |                        2514 |                                        2514 |                             2514 |                               -1160 |                                        152 |                   190 |             909 |                     317 |            1953 |              -6677 |                   811 |
| 2026-11-16 |             -980 |                        -980 |                                        -980 |                             -980 |                                -838 |                                        205 |                   188 |            -479 |                    -627 |            -776 |               5993 |                   802 |
| 2026-11-17 |            -1329 |                       -1329 |                                        2590 |                            -1329 |                               -1329 |                                        132 |                   170 |            1068 |                    -213 |             -43 |              -3557 |                  -466 |
