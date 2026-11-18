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
- 2026-11-18 SPXW: 423 snapshots, settle 7323.63 (official close), 27 trades
- 2026-11-18 SPY: 423 snapshots, settle 730.20 (official close), 27 trades

Trading days scored: **8** (verdict at 20).

| strategy                                  | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |       h1 |       h2 |
|:------------------------------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|---------:|---------:|
| B1 OR breakout                            | SPXW   | -       |        8 | 50%   |  235.75 |  -606.81 | -1513    |  1886    |  3558    | -1672    |
| B1 OR breakout                            | SPY    | -       |        8 | 62%   |   77.57 |   -19.8  |  -153.3  |   620.6  |   410.8  |   209.8  |
| B2 breakout by 11:00 only                 | SPXW   | -       |        8 | 50%   |  235.75 |  -606.81 | -1513    |  1886    |  3558    | -1672    |
| B2 breakout by 11:00 only                 | SPY    | -       |        8 | 62%   |   77.57 |   -19.8  |  -153.3  |   620.6  |   410.8  |   209.8  |
| B3 breakout with the day (vs prior close) | SPXW   | -       |        8 | 62%   |  645.75 |  -223    | -1513    |  5166    |  3438    |  1728    |
| B3 breakout with the day (vs prior close) | SPY    | -       |        8 | 62%   |  109.45 |     1.95 |  -153.3  |   875.6  |   146.8  |   728.8  |
| B4 breakout on high-VIX1D days            | SPXW   | -       |        7 | 43%   |  132.71 |  -840.14 | -1513    |   929    |  2601    | -1672    |
| B4 breakout on high-VIX1D days            | SPY    | -       |        7 | 57%   |   70.13 |   -40.59 |  -153.3  |   490.9  |   281.1  |   209.8  |
| B5 breakout, -50% stop, no target         | SPXW   | -       |        8 | 25%   | -208    | -1144.25 | -1513    | -1664    |  3348    | -5012    |
| B5 breakout, -50% stop, no target         | SPY    | -       |        8 | 38%   |   42.2  |   -86.8  |  -153.3  |   337.6  |   319.8  |    17.8  |
| F1 Reddit iron fly 14:50 (bid/ask fills)  | SPXW   | 14:50   |        8 | 100%  |  150.5  |   139.25 |   123    |  1204    |   552    |   652    |
| F1 Reddit iron fly 14:50 (bid/ask fills)  | SPY    | 14:50   |        8 | 88%   |    7.5  |    -5.85 |   -40.6  |    60    |    54.2  |     5.8  |
| F1m same, mid fills                       | SPXW   | 14:50   |        8 | 100%  |  166.12 |   151.12 |   123    |  1329    |   617    |   712    |
| F1m same, mid fills                       | SPY    | 14:50   |        8 | 88%   |    8.56 |    -4.29 |   -38.1  |    68.5  |    56.2  |    12.3  |
| I1 condor 10d                             | SPXW   | 10:00   |        8 | 100%  |  244.62 |   230.25 |   204    |  1957    |   906    |  1051    |
| I1 condor 10d                             | SPXW   | 11:30   |        8 | 88%   |   43.25 |  -273.88 | -1097.02 |   345.98 |   701    |  -355.02 |
| I1 condor 10d                             | SPXW   | 13:00   |        8 | 88%   |  144    |    73.37 |  -116.01 |  1151.99 |   280.99 |   871    |
| I1 condor 10d                             | SPXW   | 14:30   |        8 | 100%  |  143.38 |   122.75 |   104    |  1147    |   441    |   706    |
| I1 condor 10d                             | SPY    | 10:00   |        8 | 100%  |   27.52 |    24.65 |    20.4  |   220.2  |   100.6  |   119.6  |
| I1 condor 10d                             | SPY    | 11:30   |        8 | 88%   |    8.15 |   -15.11 |   -78.6  |    65.2  |    67.6  |    -2.4  |
| I1 condor 10d                             | SPY    | 13:00   |        8 | 100%  |   18.15 |    14.77 |     8.4  |   145.2  |    55.6  |    89.6  |
| I1 condor 10d                             | SPY    | 14:30   |        8 | 100%  |   12.4  |     9.52 |     5.4  |    99.2  |    35.6  |    63.6  |
| I2 condor 10d stop 2x                     | SPXW   | 10:00   |        8 | 25%   | -174.25 |  -317.62 |  -367    | -1394    |  -677    |  -717    |
| I2 condor 10d stop 2x                     | SPXW   | 11:30   |        8 | 50%   |  -15.25 |  -149.88 |  -302    |  -122    |    -6    |  -116    |
| I2 condor 10d stop 2x                     | SPXW   | 13:00   |        8 | 38%   |  -48.5  |  -171.25 |  -302    |  -388    |  -763    |   375    |
| I2 condor 10d stop 2x                     | SPXW   | 14:30   |        8 | 62%   |   -4.5  |  -120.41 |  -377    |   -36    |   215    |  -251    |
| I2 condor 10d stop 2x                     | SPY    | 10:00   |        8 | 38%   |  -14.35 |   -36.25 |   -58.2  |  -114.8  |   -90.2  |   -24.6  |
| I2 condor 10d stop 2x                     | SPY    | 11:30   |        8 | 50%   |   -3.78 |   -19.43 |   -38.2  |   -30.2  |    -3.6  |   -26.6  |
| I2 condor 10d stop 2x                     | SPY    | 13:00   |        8 | 62%   |   -0.08 |   -15.93 |   -46.2  |    -0.6  |   -24.6  |    24    |
| I2 condor 10d stop 2x                     | SPY    | 14:30   |        8 | 75%   |    1.37 |   -11.15 |   -40.2  |    11    |   -11    |    22    |
| I3 condor 20d                             | SPXW   | 10:00   |        8 | 75%   |   70.25 |  -440.25 | -1848.02 |   561.98 |   779.02 |  -217.04 |
| I3 condor 20d                             | SPXW   | 11:30   |        8 | 62%   |  -88    |  -643    | -1926    |  -703.99 |  -443    |  -260.99 |
| I3 condor 20d                             | SPXW   | 13:00   |        8 | 75%   |   76.87 |  -328.33 | -1326.01 |   614.97 | -1379.04 |  1994.01 |
| I3 condor 20d                             | SPXW   | 14:30   |        8 | 100%  |  372.75 |   319    |   219    |  2982    |  1201    |  1781    |
| I3 condor 20d                             | SPY    | 10:00   |        8 | 62%   |   28.65 |    -6.1  |   -84.6  |   229.2  |    99.6  |   129.6  |
| I3 condor 20d                             | SPY    | 11:30   |        8 | 62%   |  -14.72 |   -78.73 |  -233.6  |  -117.8  |   -52.4  |   -65.4  |
| I3 condor 20d                             | SPY    | 13:00   |        8 | 75%   |   19.15 |    -5.11 |   -48.6  |   153.2  |   -37.4  |   190.6  |
| I3 condor 20d                             | SPY    | 14:30   |        8 | 100%  |   38.9  |    32.15 |    17.4  |   311.2  |   120.6  |   190.6  |
| L1 long straddle                          | SPXW   | 10:00   |        8 | 50%   | -227.62 | -1542.45 | -2956    | -1820.98 | -1854    |    33.02 |
| L1 long straddle                          | SPXW   | 11:30   |        8 | 38%   | -112.12 | -1327.87 | -3216    |  -896.97 |  2431.01 | -3327.98 |
| L1 long straddle                          | SPXW   | 13:00   |        8 | 38%   | -347.25 | -1118.5  | -2216    | -2777.99 |  1866.01 | -4644    |
| L1 long straddle                          | SPXW   | 14:30   |        8 | 12%   | -441    |  -815.38 | -1146    | -3528    |    46    | -3574    |
| L1 long straddle                          | SPY    | 10:00   |        8 | 50%   |  -13.1  |  -145.39 |  -274.6  |  -104.8  |   -88.4  |   -16.4  |
| L1 long straddle                          | SPY    | 11:30   |        8 | 38%   |   18.4  |  -107.6  |  -230.6  |   147.2  |   216.6  |   -69.4  |
| L1 long straddle                          | SPY    | 13:00   |        8 | 38%   |  -35.85 |  -101.6  |  -211.6  |  -286.8  |   151.6  |  -438.4  |
| L1 long straddle                          | SPY    | 14:30   |        8 | 25%   |  -40.1  |   -73.35 |  -101.6  |  -320.8  |    -6.4  |  -314.4  |
| T1 trend spread 15d                       | SPXW   | 10:00   |        8 | 88%   |   24.87 |  -325.01 | -1215.02 |   198.98 |   758    |  -559.02 |
| T1 trend spread 15d                       | SPXW   | 11:30   |        8 | 88%   |   93.87 |  -101.78 |  -608.01 |   750.99 |  -147.01 |   898    |
| T1 trend spread 15d                       | SPXW   | 13:00   |        8 | 75%   |  -69.63 |  -362.38 | -1118.01 |  -557.03 | -1290.03 |   733    |
| T1 trend spread 15d                       | SPXW   | 14:30   |        8 | 100%  |  126.38 |   105.75 |    72    |  1011    |   403    |   608    |
| T1 trend spread 15d                       | SPY    | 10:00   |        8 | 100%  |   24.08 |    22.82 |    21.7  |   192.6  |    90.8  |   101.8  |
| T1 trend spread 15d                       | SPY    | 11:30   |        8 | 88%   |    9.07 |   -12.56 |   -68.3  |    72.6  |   -25.2  |    97.8  |
| T1 trend spread 15d                       | SPY    | 13:00   |        8 | 88%   |    5.7  |   -15.8  |   -71.3  |    45.6  |   -35.2  |    80.8  |
| T1 trend spread 15d                       | SPY    | 14:30   |        8 | 100%  |   12.45 |     9.95 |     4.7  |    99.6  |    37.8  |    61.8  |

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
| 2026-11-18 |            -1666 |                       -1666 |                                       -1666 |                            -1666 |                               -1666 |                                        169 |                   176 |            1047 |                    -191 |            2610 |              -8109 |                   876 |
