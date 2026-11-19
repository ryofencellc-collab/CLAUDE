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
- 2026-11-19 SPXW: 402 snapshots, settle 7175.83 (official close), 27 trades
- 2026-11-19 SPY: 402 snapshots, settle 715.87 (official close), 27 trades

Trading days scored: **9** (verdict at 20).

| strategy                                  | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |       h1 |       h2 |
|:------------------------------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|---------:|---------:|
| B1 OR breakout                            | SPXW   | -       |        9 | 56%   |  600.33 |  -369.67 | -1513    |  5403    |  3558    |  1845    |
| B1 OR breakout                            | SPY    | -       |        9 | 67%   |  105.48 |     6.78 |  -153.3  |   949.3  |   410.8  |   538.5  |
| B2 breakout by 11:00 only                 | SPXW   | -       |        9 | 56%   |  600.33 |  -369.67 | -1513    |  5403    |  3558    |  1845    |
| B2 breakout by 11:00 only                 | SPY    | -       |        9 | 67%   |  105.48 |     6.78 |  -153.3  |   949.3  |   410.8  |   538.5  |
| B3 breakout with the day (vs prior close) | SPXW   | -       |        9 | 67%   |  920.33 |    17.78 | -1513    |  8283    |  3438    |  4845    |
| B3 breakout with the day (vs prior close) | SPY    | -       |        9 | 67%   |  135.48 |    30.14 |  -153.3  |  1219.3  |   146.8  |  1072.5  |
| B4 breakout on high-VIX1D days            | SPXW   | -       |        8 | 50%   |  555.75 |  -496.81 | -1513    |  4446    |  4898    |  -452    |
| B4 breakout on high-VIX1D days            | SPY    | -       |        8 | 62%   |  102.45 |    -6.31 |  -153.3  |   819.6  |   497.8  |   321.8  |
| B5 breakout, -50% stop, no target         | SPXW   | -       |        9 | 33%   | 1444.78 |  -873.11 | -1513    | 13003    |  3348    |  9655    |
| B5 breakout, -50% stop, no target         | SPY    | -       |        9 | 44%   |  200.7  |   -39.97 |  -153.3  |  1806.3  |   319.8  |  1486.5  |
| F1 Reddit iron fly 14:50 (bid/ask fills)  | SPXW   | 14:50   |        9 | 89%   |  103.11 |    11.64 |  -276    |   928    |   552    |   376    |
| F1 Reddit iron fly 14:50 (bid/ask fills)  | SPY    | 14:50   |        9 | 78%   |    1.93 |   -10.82 |   -42.6  |    17.4  |    54.2  |   -36.8  |
| F1m same, mid fills                       | SPXW   | 14:50   |        9 | 89%   |  119.22 |    30.28 |  -256    |  1073    |   617    |   456    |
| F1m same, mid fills                       | SPY    | 14:50   |        9 | 89%   |    9.92 |    -1.61 |   -38.1  |    89.3  |    56.2  |    33.1  |
| I1 condor 10d                             | SPXW   | 10:00   |        9 | 89%   |  -25.44 |  -562.11 | -2186    |  -229    |   906    | -1135    |
| I1 condor 10d                             | SPXW   | 11:30   |        9 | 78%   | -206.67 |  -721.67 | -2206    | -1860.02 |   701    | -2561.02 |
| I1 condor 10d                             | SPXW   | 13:00   |        9 | 89%   |  157.33 |    91.22 |  -116.01 |  1415.99 |   280.99 |  1135    |
| I1 condor 10d                             | SPXW   | 14:30   |        9 | 100%  |  151.22 |   129    |   104    |  1361    |   441    |   920    |
| I1 condor 10d                             | SPY    | 10:00   |        9 | 89%   |   -5.04 |   -69.38 |  -265.6  |   -45.4  |   100.6  |  -146    |
| I1 condor 10d                             | SPY    | 11:30   |        9 | 78%   |  -22.82 |   -77.72 |  -270.6  |  -205.4  |    67.6  |  -273    |
| I1 condor 10d                             | SPY    | 13:00   |        9 | 100%  |   19.29 |    15.73 |     8.4  |   173.6  |    55.6  |   118    |
| I1 condor 10d                             | SPY    | 14:30   |        9 | 100%  |   13.96 |    10.51 |     5.4  |   125.6  |    35.6  |    90    |
| I2 condor 10d stop 2x                     | SPXW   | 10:00   |        9 | 22%   | -192.33 |  -319.22 |  -367    | -1731    |  -677    | -1054    |
| I2 condor 10d stop 2x                     | SPXW   | 11:30   |        9 | 44%   |  -62.67 |  -205.8  |  -442    |  -564    |    -6    |  -558    |
| I2 condor 10d stop 2x                     | SPXW   | 13:00   |        9 | 44%   |  -13.78 |  -134.56 |  -302    |  -124    |  -763    |   639    |
| I2 condor 10d stop 2x                     | SPXW   | 14:30   |        9 | 56%   |  -33.11 |  -144.44 |  -377    |  -298    |   215    |  -513    |
| I2 condor 10d stop 2x                     | SPY    | 10:00   |        9 | 33%   |  -17.67 |   -36.69 |   -58.2  |  -159    |   -90.2  |   -68.8  |
| I2 condor 10d stop 2x                     | SPY    | 11:30   |        9 | 44%   |   -7.71 |   -22.84 |   -39.2  |   -69.4  |    -3.6  |   -65.8  |
| I2 condor 10d stop 2x                     | SPY    | 13:00   |        9 | 67%   |    3.09 |   -12.04 |   -46.2  |    27.8  |   -24.6  |    52.4  |
| I2 condor 10d stop 2x                     | SPY    | 14:30   |        9 | 67%   |   -2.69 |   -15.38 |   -40.2  |   -24.2  |   -11    |   -13.2  |
| I3 condor 20d                             | SPXW   | 10:00   |        9 | 67%   | -131.56 |  -670.34 | -1848.02 | -1184.02 |   779.02 | -1963.04 |
| I3 condor 20d                             | SPXW   | 11:30   |        9 | 56%   | -278.89 |  -838.12 | -1926    | -2509.99 |  -443    | -2066.99 |
| I3 condor 20d                             | SPXW   | 13:00   |        9 | 78%   |  143.22 |  -227.67 | -1326.01 |  1288.97 | -1379.04 |  2668.01 |
| I3 condor 20d                             | SPXW   | 14:30   |        9 | 89%   |  239.89 |   -13.33 |  -822.99 |  2159.01 |  1201    |   958.01 |
| I3 condor 20d                             | SPY    | 10:00   |        9 | 56%   |    1.29 |   -52.5  |  -217.6  |    11.6  |    99.6  |   -88    |
| I3 condor 20d                             | SPY    | 11:30   |        9 | 56%   |  -37.82 |  -103.71 |  -233.6  |  -340.4  |   -52.4  |  -288    |
| I3 condor 20d                             | SPY    | 13:00   |        9 | 78%   |   25.18 |     1.51 |   -48.6  |   226.6  |   -37.4  |   264    |
| I3 condor 20d                             | SPY    | 14:30   |        9 | 89%   |   29.18 |    11.4  |   -48.6  |   262.6  |   120.6  |   142    |
| L1 long straddle                          | SPXW   | 10:00   |        9 | 56%   | 1337.78 | -1070.16 | -2956    | 12040    | -1854    | 13894    |
| L1 long straddle                          | SPXW   | 11:30   |        9 | 44%   |  843.78 |  -888.11 | -3216    |  7594.02 |  2431.01 |  5163.01 |
| L1 long straddle                          | SPXW   | 13:00   |        9 | 33%   | -423.78 | -1111.56 | -2216    | -3813.99 |  1866.01 | -5680    |
| L1 long straddle                          | SPXW   | 14:30   |        9 | 22%   | -364.33 |  -729.39 | -1146    | -3279    |    46    | -3325    |
| L1 long straddle                          | SPY    | 10:00   |        9 | 56%   |  143.96 |   -96.16 |  -274.6  |  1295.6  |   -88.4  |  1384    |
| L1 long straddle                          | SPY    | 11:30   |        9 | 44%   |  101.07 |   -62.72 |  -230.6  |   909.6  |   216.6  |   693    |
| L1 long straddle                          | SPY    | 13:00   |        9 | 33%   |  -49.93 |  -111.82 |  -211.6  |  -449.4  |   151.6  |  -601    |
| L1 long straddle                          | SPY    | 14:30   |        9 | 33%   |  -34.04 |   -66.04 |  -101.6  |  -306.4  |    -6.4  |  -300    |
| T1 trend spread 15d                       | SPXW   | 10:00   |        9 | 89%   |   52.33 |  -260.34 | -1215.02 |   470.98 |   758    |  -287.02 |
| T1 trend spread 15d                       | SPXW   | 11:30   |        9 | 89%   |  110.33 |   -64.11 |  -608.01 |   992.99 |  -147.01 |  1140    |
| T1 trend spread 15d                       | SPXW   | 13:00   |        9 | 78%   |  -34.45 |  -296.18 | -1118.01 |  -310.03 | -1290.03 |   980    |
| T1 trend spread 15d                       | SPXW   | 14:30   |        9 | 100%  |  134.22 |   111.44 |    72    |  1208    |   403    |   805    |
| T1 trend spread 15d                       | SPY    | 10:00   |        9 | 100%  |   24.37 |    23.14 |    21.7  |   219.3  |    90.8  |   128.5  |
| T1 trend spread 15d                       | SPY    | 11:30   |        9 | 89%   |   10.7  |    -8.41 |   -68.3  |    96.3  |   -25.2  |   121.5  |
| T1 trend spread 15d                       | SPY    | 13:00   |        9 | 89%   |    8.37 |   -10.97 |   -71.3  |    75.3  |   -35.2  |   110.5  |
| T1 trend spread 15d                       | SPY    | 14:30   |        9 | 100%  |   13.37 |    10.59 |     4.7  |   120.3  |    37.8  |    82.5  |

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
| 2026-11-19 |             3846 |                        3846 |                                        3461 |                             3846 |                               16136 |                                       -319 |                  -235 |           -4395 |                    -867 |           -4116 |              23580 |                  1059 |
