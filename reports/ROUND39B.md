# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.94 (official close), 21 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.69 (official close), 21 trades
- 2026-11-10 SPXW: 434 snapshots, settle 7520.93 (official close), 21 trades
- 2026-11-10 SPY: 427 snapshots, settle 749.92 (official close), 21 trades
- 2026-11-11 SPXW: 439 snapshots, settle 7619.38 (official close), 21 trades
- 2026-11-11 SPY: 439 snapshots, settle 759.81 (official close), 21 trades
- 2026-11-12 SPXW: 439 snapshots, settle 7592.40 (official close), 21 trades
- 2026-11-12 SPY: 439 snapshots, settle 757.12 (official close), 21 trades
- 2026-11-13 SPXW: 438 snapshots, settle 7561.67 (official close), 21 trades
- 2026-11-13 SPY: 438 snapshots, settle 754.37 (official close), 21 trades
- 2026-11-16 SPXW: 438 snapshots, settle 7416.59 (official close), 21 trades
- 2026-11-16 SPY: 438 snapshots, settle 739.95 (official close), 21 trades
- 2026-11-17 SPXW: 435 snapshots, settle 7340.53 (official close), 21 trades
- 2026-11-17 SPY: 428 snapshots, settle 732.44 (official close), 21 trades

Trading days scored: **7** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |      h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|--------:|---------:|
| B1 OR breakout        | SPXW   | -       |        7 | 86%   | 1495.57 |   737    | -1023    | 10469    | 2261    |  8208    |
| B1 OR breakout        | SPY    | -       |        7 | 57%   |   84.56 |   -20.19 |  -135.3  |   591.9  |   68.1  |   523.8  |
| I1 condor 10d         | SPXW   | 10:00   |        7 | 100%  |  257.57 |   241.14 |   214    |  1803    |  752    |  1051    |
| I1 condor 10d         | SPXW   | 11:30   |        7 | 100%  |  214    |   189    |   139    |  1498    |  562    |   936    |
| I1 condor 10d         | SPXW   | 13:00   |        7 | 71%   |  -11.43 |  -218.69 |  -606.01 |   -80.03 | -126.02 |    45.99 |
| I1 condor 10d         | SPXW   | 14:30   |        7 | 100%  |  145.43 |   122.57 |    89    |  1018    |  347    |   671    |
| I1 condor 10d         | SPY    | 10:00   |        7 | 100%  |   26.4  |    23.97 |    22.4  |   184.8  |   78.2  |   106.6  |
| I1 condor 10d         | SPY    | 11:30   |        7 | 100%  |   21.54 |    17.69 |    12.4  |   150.8  |   47.2  |   103.6  |
| I1 condor 10d         | SPY    | 13:00   |        7 | 100%  |   17.54 |    14.4  |    10.4  |   122.8  |   45.2  |    77.6  |
| I1 condor 10d         | SPY    | 14:30   |        7 | 100%  |   13.83 |    11.54 |     8.4  |    96.8  |   36.2  |    60.6  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        7 | 14%   | -239.71 |  -344.86 |  -382    | -1678    | -330    | -1348    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        7 | 57%   |    7.86 |  -160.33 |  -392    |    55    | -350    |   405    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        7 | 43%   |  -49.43 |  -174.71 |  -262    |  -346    | -340    |    -6    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        7 | 71%   |   50.14 |   -52.29 |  -237    |   351    |  111    |   240    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        7 | 29%   |  -20.17 |   -39.06 |   -51.2  |  -141.2  |  -58    |   -83.2  |
| I2 condor 10d stop 2x | SPY    | 11:30   |        7 | 57%   |    1    |   -15.6  |   -37.2  |     7    |  -31    |    38    |
| I2 condor 10d stop 2x | SPY    | 13:00   |        7 | 57%   |    1.43 |   -12.74 |   -31.2  |    10    |   16.6  |    -6.6  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        7 | 57%   |   -6.86 |   -21.31 |   -38.2  |   -48    |  -10.4  |   -37.6  |
| I3 condor 20d         | SPXW   | 10:00   |        7 | 43%   | -222.29 |  -781.14 | -1841    | -1556    | -619.98 |  -936.02 |
| I3 condor 20d         | SPXW   | 11:30   |        7 | 57%   |  -75    |  -575.29 | -1246.01 |  -525.02 | 1397    | -1922.02 |
| I3 condor 20d         | SPXW   | 13:00   |        7 | 57%   | -295.15 |  -904.15 | -1881.01 | -2066.05 | -911.02 | -1155.03 |
| I3 condor 20d         | SPXW   | 14:30   |        7 | 100%  |  317.85 |   232.85 |   108.99 |  2224.97 |  778.98 |  1445.99 |
| I3 condor 20d         | SPY    | 10:00   |        7 | 57%   |   -4.74 |   -73.6  |  -233.6  |   -33.2  |   34.2  |   -67.4  |
| I3 condor 20d         | SPY    | 11:30   |        7 | 71%   |   24.11 |    -1.89 |   -38.6  |   168.8  |  139.2  |    29.6  |
| I3 condor 20d         | SPY    | 13:00   |        7 | 71%   |   -3.89 |   -60.31 |  -148.6  |   -27.2  |  -54.8  |    27.6  |
| I3 condor 20d         | SPY    | 14:30   |        7 | 100%  |   44.69 |    37.11 |    27.4  |   312.8  |  101.2  |   211.6  |
| L1 long straddle      | SPXW   | 10:00   |        7 | 57%   |  624    | -1342.43 | -3676    |  4368    | 1227    |  3141    |
| L1 long straddle      | SPXW   | 11:30   |        7 | 57%   |  273.29 |  -894.57 | -2191    |  1913    |  252    |  1661    |
| L1 long straddle      | SPXW   | 13:00   |        7 | 57%   |  286.14 |  -528.86 | -1441    |  2003    | 1552    |   451    |
| L1 long straddle      | SPXW   | 14:30   |        7 | 29%   | -206.71 |  -580.36 |  -906    | -1447    |  232    | -1679    |
| L1 long straddle      | SPY    | 10:00   |        7 | 57%   |   63.69 |  -128.03 |  -346.6  |   445.8  |  126.2  |   319.6  |
| L1 long straddle      | SPY    | 11:30   |        7 | 57%   |   15.26 |   -79.6  |  -186.6  |   106.8  |   20.2  |    86.6  |
| L1 long straddle      | SPY    | 13:00   |        7 | 57%   |   10.4  |   -60.03 |  -140.6  |    72.8  |   81.2  |    -8.4  |
| L1 long straddle      | SPY    | 14:30   |        7 | 29%   |  -22.6  |   -55.46 |   -91.6  |  -158.2  |  -18.8  |  -139.4  |
| T1 trend spread 15d   | SPXW   | 10:00   |        7 | 86%   | -130.29 |  -788.44 | -2114.02 |  -912.02 |  576    | -1488.02 |
| T1 trend spread 15d   | SPXW   | 11:30   |        7 | 86%   |   67    |  -148    |  -598.01 |   468.99 |  426    |    42.99 |
| T1 trend spread 15d   | SPXW   | 13:00   |        7 | 71%   | -255.58 |  -737.58 | -1608.01 | -1789.03 | -732.02 | -1057.01 |
| T1 trend spread 15d   | SPXW   | 14:30   |        7 | 100%  |  124.14 |   101.29 |    57    |   869    |  306    |   563    |
| T1 trend spread 15d   | SPY    | 10:00   |        7 | 86%   |   -5.73 |   -62.73 |  -178.3  |   -40.1  |   68.1  |  -108.2  |
| T1 trend spread 15d   | SPY    | 11:30   |        7 | 100%  |   17.27 |    14.27 |     9.7  |   120.9  |   43.1  |    77.8  |
| T1 trend spread 15d   | SPY    | 13:00   |        7 | 71%   |   -9.73 |   -36.87 |   -77.3  |   -68.1  |  -47.9  |   -20.2  |
| T1 trend spread 15d   | SPY    | 14:30   |        7 | 100%  |   12.56 |     9.41 |     3.7  |    87.9  |   27.1  |    60.8  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             345 |                     462 |            -199 |              -5231 |                  -497 |
| 2026-11-11 |              858 |             648 |                    -245 |             807 |                257 |                   588 |
| 2026-11-12 |             1649 |              25 |                    -302 |           -2454 |               1332 |                 -1946 |
| 2026-11-13 |             2341 |             944 |                     383 |            1612 |              -3783 |                   811 |
| 2026-11-16 |             2661 |            1018 |                    -746 |           -3157 |               7945 |                 -1729 |
| 2026-11-17 |             2082 |            1067 |                    -134 |            1635 |              -1660 |                   936 |
