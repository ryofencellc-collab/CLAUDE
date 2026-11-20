# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.94 (official close), 35 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.69 (official close), 35 trades
- 2026-11-10 SPXW: 419 snapshots, settle 7520.93 (official close), 36 trades
- 2026-11-10 SPY: 412 snapshots, settle 749.92 (official close), 35 trades
- 2026-11-11 SPXW: 424 snapshots, settle 7619.38 (official close), 30 trades
- 2026-11-11 SPY: 424 snapshots, settle 759.81 (official close), 30 trades
- 2026-11-12 SPXW: 424 snapshots, settle 7592.40 (official close), 34 trades
- 2026-11-12 SPY: 424 snapshots, settle 757.12 (official close), 35 trades
- 2026-11-13 SPXW: 423 snapshots, settle 7561.67 (official close), 39 trades
- 2026-11-13 SPY: 423 snapshots, settle 754.37 (official close), 38 trades
- 2026-11-16 SPXW: 423 snapshots, settle 7416.59 (official close), 42 trades
- 2026-11-16 SPY: 423 snapshots, settle 739.95 (official close), 41 trades
- 2026-11-17 SPXW: 420 snapshots, settle 7340.53 (official close), 48 trades
- 2026-11-17 SPY: 413 snapshots, settle 732.44 (official close), 47 trades
- 2026-11-18 SPXW: 423 snapshots, settle 7323.63 (official close), 31 trades
- 2026-11-18 SPY: 423 snapshots, settle 730.20 (official close), 31 trades
- 2026-11-19 SPXW: 402 snapshots, settle 7175.83 (official close), 59 trades
- 2026-11-19 SPY: 402 snapshots, settle 715.87 (official close), 57 trades

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
| S1 trend-pullback scalper                 | SPXW   | 10:06   |        1 | 100%  |  637    |   nan    |   637    |   637    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:12   |        2 | 50%   |  147    |   nan    |  -423    |   294    |  -423    |   717    |
| S1 trend-pullback scalper                 | SPXW   | 10:13   |        1 | 100%  |  547    |   nan    |   547    |   547    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:24   |        1 | 100%  |  597    |   nan    |   597    |   597    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:25   |        1 | 0%    | -523    |   nan    |  -523    |  -523    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:29   |        1 | 0%    | -373    |   nan    |  -373    |  -373    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:30   |        1 | 0%    | -543    |   nan    |  -543    |  -543    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:32   |        1 | 100%  |  537    |   nan    |   537    |   537    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:40   |        1 | 0%    | -973    |   nan    |  -973    |  -973    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:45   |        2 | 0%    | -203    |   nan    |  -293    |  -406    |  -293    |  -113    |
| S1 trend-pullback scalper                 | SPXW   | 10:47   |        1 | 0%    | -463    |   nan    |  -463    |  -463    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:50   |        1 | 100%  |  817    |   nan    |   817    |   817    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:53   |        1 | 100%  |  747    |   nan    |   747    |   747    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:56   |        1 | 0%    | -413    |   nan    |  -413    |  -413    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:57   |        1 | 0%    | -543    |   nan    |  -543    |  -543    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 10:58   |        1 | 0%    | -713    |   nan    |  -713    |  -713    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:02   |        1 | 100%  |  827    |   nan    |   827    |   827    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:03   |        1 | 0%    | -713    |   nan    |  -713    |  -713    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:04   |        1 | 0%    | -283    |   nan    |  -283    |  -283    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:05   |        1 | 0%    | -243    |   nan    |  -243    |  -243    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:07   |        1 | 100%  |  467    |   nan    |   467    |   467    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:11   |        1 | 0%    |  -73    |   nan    |   -73    |   -73    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:14   |        1 | 0%    | -113    |   nan    |  -113    |  -113    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:18   |        1 | 0%    | -423    |   nan    |  -423    |  -423    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:22   |        3 | 0%    | -463    |  -546.33 |  -593    | -1389    |  -343    | -1046    |
| S1 trend-pullback scalper                 | SPXW   | 11:23   |        1 | 0%    | -373    |   nan    |  -373    |  -373    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:26   |        2 | 0%    | -328    |   nan    |  -403    |  -656    |  -253    |  -403    |
| S1 trend-pullback scalper                 | SPXW   | 11:27   |        1 | 0%    | -453    |   nan    |  -453    |  -453    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:29   |        1 | 100%  |  517    |   nan    |   517    |   517    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:30   |        1 | 100%  |   87    |   nan    |    87    |    87    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:32   |        1 | 0%    | -253    |   nan    |  -253    |  -253    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:33   |        1 | 0%    | -513    |   nan    |  -513    |  -513    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:38   |        1 | 100%  |  297    |   nan    |   297    |   297    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:42   |        1 | 100%  |  427    |   nan    |   427    |   427    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:46   |        1 | 100%  |  597    |   nan    |   597    |   597    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:47   |        1 | 100%  |  547    |   nan    |   547    |   547    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:49   |        1 | 100%  |  907    |   nan    |   907    |   907    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:53   |        1 | 100%  |  507    |   nan    |   507    |   507    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:54   |        2 | 100%  |  472    |   nan    |    87    |   944    |    87    |   857    |
| S1 trend-pullback scalper                 | SPXW   | 11:56   |        1 | 0%    | -553    |   nan    |  -553    |  -553    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:57   |        1 | 100%  |  407    |   nan    |   407    |   407    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 11:58   |        1 | 0%    | -563    |   nan    |  -563    |  -563    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:00   |        1 | 100%  |  637    |   nan    |   637    |   637    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:01   |        1 | 0%    | -223    |   nan    |  -223    |  -223    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:05   |        2 | 0%    | -543    |   nan    |  -713    | -1086    |  -373    |  -713    |
| S1 trend-pullback scalper                 | SPXW   | 12:08   |        2 | 0%    | -583    |   nan    |  -693    | -1166    |  -473    |  -693    |
| S1 trend-pullback scalper                 | SPXW   | 12:10   |        1 | 0%    | -213    |   nan    |  -213    |  -213    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:12   |        1 | 100%  |  197    |   nan    |   197    |   197    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:17   |        1 | 0%    | -413    |   nan    |  -413    |  -413    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:18   |        1 | 100%  |  397    |   nan    |   397    |   397    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:20   |        1 | 0%    | -693    |   nan    |  -693    |  -693    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:23   |        1 | 0%    | -603    |   nan    |  -603    |  -603    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:25   |        1 | 0%    | -253    |   nan    |  -253    |  -253    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:26   |        1 | 0%    | -513    |   nan    |  -513    |  -513    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:31   |        1 | 100%  |  357    |   nan    |   357    |   357    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:32   |        1 | 100%  |  717    |   nan    |   717    |   717    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:46   |        1 | 100%  |  277    |   nan    |   277    |   277    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:48   |        1 | 0%    | -433    |   nan    |  -433    |  -433    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:51   |        1 | 0%    | -243    |   nan    |  -243    |  -243    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:53   |        1 | 100%  |  477    |   nan    |   477    |   477    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:57   |        1 | 100%  |  337    |   nan    |   337    |   337    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 12:59   |        1 | 0%    | -193    |   nan    |  -193    |  -193    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:02   |        1 | 100%  |  827    |   nan    |   827    |   827    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:06   |        1 | 100%  |  197    |   nan    |   197    |   197    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:07   |        1 | 0%    | -193    |   nan    |  -193    |  -193    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:10   |        1 | 100%  |  687    |   nan    |   687    |   687    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:20   |        1 | 0%    | -393    |   nan    |  -393    |  -393    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:24   |        2 | 50%   |  -43    |   nan    |  -393    |   -86    |   307    |  -393    |
| S1 trend-pullback scalper                 | SPXW   | 13:25   |        1 | 0%    | -383    |   nan    |  -383    |  -383    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:29   |        1 | 0%    | -393    |   nan    |  -393    |  -393    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:30   |        1 | 0%    | -203    |   nan    |  -203    |  -203    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:34   |        1 | 100%  |  527    |   nan    |   527    |   527    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:36   |        1 | 100%  |  687    |   nan    |   687    |   687    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:38   |        1 | 0%    | -173    |   nan    |  -173    |  -173    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:43   |        1 | 0%    | -243    |   nan    |  -243    |  -243    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:48   |        1 | 0%    | -203    |   nan    |  -203    |  -203    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:50   |        1 | 0%    | -223    |   nan    |  -223    |  -223    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 13:54   |        1 | 0%    | -283    |   nan    |  -283    |  -283    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:03   |        1 | 100%  |  697    |   nan    |   697    |   697    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:04   |        1 | 0%    | -143    |   nan    |  -143    |  -143    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:08   |        1 | 0%    | -153    |   nan    |  -153    |  -153    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:11   |        1 | 0%    | -313    |   nan    |  -313    |  -313    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:14   |        1 | 0%    | -333    |   nan    |  -333    |  -333    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:17   |        1 | 100%  |  327    |   nan    |   327    |   327    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:18   |        1 | 0%    |  -83    |   nan    |   -83    |   -83    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:19   |        1 | 100%  |   67    |   nan    |    67    |    67    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:22   |        1 | 0%    | -363    |   nan    |  -363    |  -363    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:27   |        1 | 100%  |  547    |   nan    |   547    |   547    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:33   |        1 | 100%  |  757    |   nan    |   757    |   757    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:44   |        1 | 0%    | -233    |   nan    |  -233    |  -233    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:46   |        1 | 100%  |  437    |   nan    |   437    |   437    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:50   |        1 | 0%    | -353    |   nan    |  -353    |  -353    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:53   |        1 | 0%    | -173    |   nan    |  -173    |  -173    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:54   |        1 | 100%  |  237    |   nan    |   237    |   237    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 14:57   |        1 | 100%  |  247    |   nan    |   247    |   247    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 15:04   |        1 | 0%    | -223    |   nan    |  -223    |  -223    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 15:07   |        1 | 0%    | -293    |   nan    |  -293    |  -293    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 15:08   |        1 | 100%  |  327    |   nan    |   327    |   327    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 15:19   |        1 | 100%  |  207    |   nan    |   207    |   207    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 15:21   |        1 | 0%    |  -63    |   nan    |   -63    |   -63    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 15:22   |        1 | 0%    | -123    |   nan    |  -123    |  -123    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 15:25   |        1 | 100%  |  267    |   nan    |   267    |   267    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPXW   | 15:27   |        1 | 100%  |  217    |   nan    |   217    |   217    |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:12   |        1 | 100%  |   67.7  |   nan    |    67.7  |    67.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:13   |        1 | 100%  |   35.7  |   nan    |    35.7  |    35.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:14   |        1 | 0%    |  -36.3  |   nan    |   -36.3  |   -36.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:16   |        1 | 100%  |   65.7  |   nan    |    65.7  |    65.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:24   |        1 | 100%  |   77.7  |   nan    |    77.7  |    77.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:25   |        1 | 0%    |  -42.3  |   nan    |   -42.3  |   -42.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:29   |        1 | 0%    |  -35.3  |   nan    |   -35.3  |   -35.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:30   |        1 | 0%    |  -56.3  |   nan    |   -56.3  |   -56.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:32   |        1 | 100%  |   11.7  |   nan    |    11.7  |    11.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:34   |        1 | 100%  |   62.7  |   nan    |    62.7  |    62.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:35   |        1 | 100%  |   14.7  |   nan    |    14.7  |    14.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:40   |        1 | 0%    |  -61.3  |   nan    |   -61.3  |   -61.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:44   |        1 | 100%  |   89.7  |   nan    |    89.7  |    89.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:45   |        1 | 0%    |  -32.3  |   nan    |   -32.3  |   -32.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:48   |        1 | 100%  |   98.7  |   nan    |    98.7  |    98.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:49   |        1 | 0%    |  -42.3  |   nan    |   -42.3  |   -42.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:50   |        1 | 100%  |   99.7  |   nan    |    99.7  |    99.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:53   |        1 | 0%    |  -74.3  |   nan    |   -74.3  |   -74.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:56   |        1 | 0%    |  -71.3  |   nan    |   -71.3  |   -71.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:57   |        1 | 0%    |  -43.3  |   nan    |   -43.3  |   -43.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 10:59   |        1 | 0%    |  -62.3  |   nan    |   -62.3  |   -62.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:00   |        1 | 0%    |  -63.3  |   nan    |   -63.3  |   -63.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:03   |        1 | 0%    |  -30.3  |   nan    |   -30.3  |   -30.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:04   |        1 | 100%  |   61.7  |   nan    |    61.7  |    61.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:05   |        3 | 33%   |    9.03 |   -32.97 |   -34.3  |    27.1  |   -30.3  |    57.4  |
| S1 trend-pullback scalper                 | SPY    | 11:07   |        1 | 100%  |   54.7  |   nan    |    54.7  |    54.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:09   |        1 | 100%  |   28.7  |   nan    |    28.7  |    28.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:11   |        1 | 0%    |   -4.3  |   nan    |    -4.3  |    -4.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:14   |        1 | 100%  |   87.7  |   nan    |    87.7  |    87.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:16   |        1 | 0%    |  -19.3  |   nan    |   -19.3  |   -19.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:22   |        1 | 0%    |  -49.3  |   nan    |   -49.3  |   -49.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:24   |        1 | 0%    |  -49.3  |   nan    |   -49.3  |   -49.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:26   |        2 | 0%    |  -40.3  |   nan    |   -57.3  |   -80.6  |   -23.3  |   -57.3  |
| S1 trend-pullback scalper                 | SPY    | 11:28   |        1 | 0%    |  -38.3  |   nan    |   -38.3  |   -38.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:29   |        3 | 33%   |   -1.97 |   -46.3  |   -59.3  |    -5.9  |   -20.3  |    14.4  |
| S1 trend-pullback scalper                 | SPY    | 11:32   |        1 | 0%    |  -25.3  |   nan    |   -25.3  |   -25.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:38   |        1 | 0%    |  -61.3  |   nan    |   -61.3  |   -61.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:39   |        1 | 100%  |   22.7  |   nan    |    22.7  |    22.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:41   |        1 | 100%  |   14.7  |   nan    |    14.7  |    14.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:46   |        1 | 100%  |   59.7  |   nan    |    59.7  |    59.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:47   |        2 | 100%  |   85.2  |   nan    |    14.7  |   170.4  |    14.7  |   155.7  |
| S1 trend-pullback scalper                 | SPY    | 11:53   |        1 | 100%  |   58.7  |   nan    |    58.7  |    58.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:54   |        2 | 50%   |  -26.3  |   nan    |   -55.3  |   -52.6  |     2.7  |   -55.3  |
| S1 trend-pullback scalper                 | SPY    | 11:56   |        1 | 100%  |   12.7  |   nan    |    12.7  |    12.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 11:58   |        2 | 0%    |  -38.8  |   nan    |   -47.3  |   -77.6  |   -47.3  |   -30.3  |
| S1 trend-pullback scalper                 | SPY    | 12:02   |        1 | 0%    |  -28.3  |   nan    |   -28.3  |   -28.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:05   |        1 | 0%    |  -69.3  |   nan    |   -69.3  |   -69.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:06   |        1 | 0%    |  -30.3  |   nan    |   -30.3  |   -30.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:07   |        1 | 0%    |  -79.3  |   nan    |   -79.3  |   -79.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:08   |        1 | 0%    |  -42.3  |   nan    |   -42.3  |   -42.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:10   |        1 | 0%    |  -15.3  |   nan    |   -15.3  |   -15.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:11   |        1 | 0%    |   -7.3  |   nan    |    -7.3  |    -7.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:18   |        1 | 100%  |   19.7  |   nan    |    19.7  |    19.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:21   |        1 | 0%    |  -50.3  |   nan    |   -50.3  |   -50.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:22   |        1 | 0%    |  -45.3  |   nan    |   -45.3  |   -45.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:23   |        1 | 0%    |  -53.3  |   nan    |   -53.3  |   -53.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:26   |        2 | 0%    |  -12.3  |   nan    |   -22.3  |   -24.6  |   -22.3  |    -2.3  |
| S1 trend-pullback scalper                 | SPY    | 12:48   |        1 | 0%    |  -47.3  |   nan    |   -47.3  |   -47.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:52   |        1 | 0%    |  -24.3  |   nan    |   -24.3  |   -24.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:55   |        1 | 100%  |   75.7  |   nan    |    75.7  |    75.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 12:59   |        1 | 0%    |  -21.3  |   nan    |   -21.3  |   -21.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:02   |        1 | 100%  |   80.7  |   nan    |    80.7  |    80.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:05   |        1 | 100%  |   12.7  |   nan    |    12.7  |    12.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:11   |        1 | 100%  |   32.7  |   nan    |    32.7  |    32.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:20   |        1 | 0%    |  -64.3  |   nan    |   -64.3  |   -64.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:23   |        1 | 0%    |  -19.3  |   nan    |   -19.3  |   -19.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:25   |        1 | 0%    |  -35.3  |   nan    |   -35.3  |   -35.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:26   |        1 | 0%    |  -40.3  |   nan    |   -40.3  |   -40.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:30   |        2 | 0%    |  -35.8  |   nan    |   -48.3  |   -71.6  |   -23.3  |   -48.3  |
| S1 trend-pullback scalper                 | SPY    | 13:35   |        1 | 0%    |  -34.3  |   nan    |   -34.3  |   -34.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:37   |        1 | 0%    |   -1.3  |   nan    |    -1.3  |    -1.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:42   |        1 | 0%    |  -27.3  |   nan    |   -27.3  |   -27.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:44   |        1 | 0%    |  -23.3  |   nan    |   -23.3  |   -23.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:48   |        1 | 0%    |  -46.3  |   nan    |   -46.3  |   -46.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:51   |        1 | 100%  |   31.7  |   nan    |    31.7  |    31.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 13:54   |        1 | 100%  |   46.7  |   nan    |    46.7  |    46.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:05   |        1 | 0%    |  -17.3  |   nan    |   -17.3  |   -17.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:09   |        1 | 0%    |  -15.3  |   nan    |   -15.3  |   -15.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:11   |        1 | 0%    |  -40.3  |   nan    |   -40.3  |   -40.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:18   |        1 | 100%  |   52.7  |   nan    |    52.7  |    52.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:19   |        1 | 0%    |  -15.3  |   nan    |   -15.3  |   -15.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:20   |        1 | 0%    |  -36.3  |   nan    |   -36.3  |   -36.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:26   |        1 | 0%    |  -44.3  |   nan    |   -44.3  |   -44.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:29   |        1 | 100%  |   64.7  |   nan    |    64.7  |    64.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:32   |        1 | 100%  |    5.7  |   nan    |     5.7  |     5.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:44   |        1 | 0%    |  -26.3  |   nan    |   -26.3  |   -26.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:49   |        1 | 100%  |   38.7  |   nan    |    38.7  |    38.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:51   |        1 | 0%    |  -20.3  |   nan    |   -20.3  |   -20.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 14:54   |        2 | 50%   |    3.2  |   nan    |   -19.3  |     6.4  |    25.7  |   -19.3  |
| S1 trend-pullback scalper                 | SPY    | 15:04   |        1 | 0%    |  -37.3  |   nan    |   -37.3  |   -37.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 15:07   |        1 | 0%    |  -28.3  |   nan    |   -28.3  |   -28.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 15:19   |        1 | 100%  |   25.7  |   nan    |    25.7  |    25.7  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 15:21   |        2 | 0%    |  -37.8  |   nan    |   -48.3  |   -75.6  |   -27.3  |   -48.3  |
| S1 trend-pullback scalper                 | SPY    | 15:22   |        1 | 0%    |  -10.3  |   nan    |   -10.3  |   -10.3  |   nan    |   nan    |
| S1 trend-pullback scalper                 | SPY    | 15:27   |        1 | 100%  |   28.7  |   nan    |    28.7  |    28.7  |   nan    |   nan    |
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

| day        |   B1 OR breakout |   B2 breakout by 11:00 only |   B3 breakout with the day (vs prior close) |   B4 breakout on high-VIX1D days |   B5 breakout, -50% stop, no target |   F1 Reddit iron fly 14:50 (bid/ask fills) |   F1m same, mid fills |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   S1 trend-pullback scalper |   T1 trend spread 15d |
|:-----------|-----------------:|----------------------------:|--------------------------------------------:|---------------------------------:|------------------------------------:|-------------------------------------------:|----------------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------------:|----------------------:|
| 2026-11-09 |             2259 |                        2259 |                                        2259 |                             2259 |                                4496 |                                        170 |                   214 |             686 |                   -1038 |             186 |               6242 |                         170 |                   592 |
| 2026-11-10 |            -1221 |                       -1221 |                                       -1115 |                            -1221 |                               -1221 |                                        147 |                   160 |             807 |                     386 |             888 |              -3948 |                        -552 |                   162 |
| 2026-11-11 |             1087 |                        1087 |                                        1087 |                              nan |                                1227 |                                        135 |                   133 |             603 |                    -479 |             950 |               -801 |                        -306 |                   529 |
| 2026-11-12 |             1845 |                        1845 |                                        1355 |                             1845 |                                -833 |                                        155 |                   166 |             494 |                    -230 |           -1734 |               1271 |                        -205 |                 -1490 |
| 2026-11-13 |             2514 |                        2514 |                                        2514 |                             2514 |                               -1160 |                                        152 |                   190 |             909 |                     317 |            1953 |              -6677 |                        -989 |                   811 |
| 2026-11-16 |             -980 |                        -980 |                                        -980 |                             -980 |                                -838 |                                        205 |                   188 |            -479 |                    -627 |            -776 |               5993 |                        -451 |                   802 |
| 2026-11-17 |            -1329 |                       -1329 |                                        2590 |                            -1329 |                               -1329 |                                        132 |                   170 |            1068 |                    -213 |             -43 |              -3557 |                         168 |                  -466 |
| 2026-11-18 |            -1666 |                       -1666 |                                       -1666 |                            -1666 |                               -1666 |                                        169 |                   176 |            1047 |                    -191 |            2610 |              -8109 |                       -1039 |                   876 |
| 2026-11-19 |             3846 |                        3846 |                                        3461 |                             3846 |                               16136 |                                       -319 |                  -235 |           -4395 |                    -867 |           -4116 |              23580 |                         722 |                  1059 |
