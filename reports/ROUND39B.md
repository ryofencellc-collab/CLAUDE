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
- 2026-11-16 SPXW: 270 snapshots, settle 7418.71 (official close), 16 trades
- 2026-11-16 SPY: 270 snapshots, settle 739.93 (official close), 16 trades

Trading days scored: **6** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |      h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|--------:|---------:|
| B1 OR breakout        | SPXW   | -       |        6 | 83%   | 1375.33 |   507    | -1023    |  8252    | 2261    |  5991    |
| B1 OR breakout        | SPY    | -       |        6 | 67%   |  121.2  |     7.53 |  -107.3  |   727.2  |   68.1  |   659.1  |
| I1 condor 10d         | SPXW   | 10:00   |        6 | 100%  |  253.17 |   235.67 |   214    |  1519    |  752    |   767    |
| I1 condor 10d         | SPXW   | 11:30   |        6 | 100%  |  209    |   182.33 |   139    |  1254    |  562    |   692    |
| I1 condor 10d         | SPXW   | 13:00   |        6 | 67%   |  -52.34 |  -276.18 |  -606.01 |  -314.03 | -126.02 |  -188.01 |
| I1 condor 10d         | SPXW   | 14:30   |        5 | 100%  |  126    |   109    |    89    |   630    |  228    |   402    |
| I1 condor 10d         | SPY    | 10:00   |        6 | 100%  |   25.4  |    23.57 |    22.4  |   152.4  |   78.2  |    74.2  |
| I1 condor 10d         | SPY    | 11:30   |        6 | 100%  |   19.9  |    16.57 |    12.4  |   119.4  |   47.2  |    72.2  |
| I1 condor 10d         | SPY    | 13:00   |        6 | 100%  |   16.23 |    13.4  |    10.4  |    97.4  |   45.2  |    52.2  |
| I1 condor 10d         | SPY    | 14:30   |        5 | 100%  |   12    |    10.4  |     8.4  |    60    |   23.8  |    36.2  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        6 | 33%   | -115.83 |  -312    |  -382    |  -695    | -330    |  -365    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        6 | 67%   |   57    |  -116.67 |  -392    |   342    | -350    |   692    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        6 | 50%   |  -22.33 |  -159.33 |  -262    |  -134    | -340    |   206    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        5 | 80%   |   78.8  |   -28.6  |  -147    |   394    |   -8    |   402    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        6 | 33%   |  -16.33 |   -37.37 |   -51.2  |   -98    |  -58    |   -40    |
| I2 condor 10d stop 2x | SPY    | 11:30   |        6 | 67%   |    6.87 |    -9.5  |   -28.2  |    41.2  |  -31    |    72.2  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        6 | 67%   |    5.7  |    -7.5  |   -22.2  |    34.2  |   16.6  |    17.6  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        5 | 80%   |    2.68 |   -17.36 |   -38.2  |    13.4  |  -22.8  |    36.2  |
| I3 condor 20d         | SPXW   | 10:00   |        6 | 50%   | -208.83 |  -859.88 | -1841    | -1252.98 | -619.98 |  -633    |
| I3 condor 20d         | SPXW   | 11:30   |        6 | 50%   | -155.33 |  -645.83 | -1246.01 |  -932    | 1397    | -2329    |
| I3 condor 20d         | SPXW   | 13:00   |        6 | 50%   | -403    | -1082.68 | -1881.01 | -2418.03 | -911.02 | -1507.01 |
| I3 condor 20d         | SPXW   | 14:30   |        5 | 100%  |  257.39 |   178.99 |   108.99 |  1286.97 |  399.98 |   886.99 |
| I3 condor 20d         | SPY    | 10:00   |        6 | 50%   |   -9.93 |   -94.27 |  -233.6  |   -59.6  |   34.2  |   -93.8  |
| I3 condor 20d         | SPY    | 11:30   |        6 | 67%   |   15.07 |   -11.43 |   -40.6  |    90.4  |  139.2  |   -48.8  |
| I3 condor 20d         | SPY    | 13:00   |        6 | 67%   |  -16.77 |   -78.94 |  -148.6  |  -100.6  |  -54.8  |   -45.8  |
| I3 condor 20d         | SPY    | 14:30   |        5 | 100%  |   38.4  |    32.8  |    27.4  |   192    |   68.8  |   123.2  |
| L1 long straddle      | SPXW   | 10:00   |        6 | 50%   |  268.83 | -1820.17 | -3676    |  1613    | 1227    |   386    |
| L1 long straddle      | SPXW   | 11:30   |        6 | 67%   |  625.5  |  -443.17 | -2066    |  3753    |  252    |  3501    |
| L1 long straddle      | SPXW   | 13:00   |        6 | 67%   |  492.17 |  -269.5  | -1311    |  2953    | 1552    |  1401    |
| L1 long straddle      | SPXW   | 14:30   |        5 | 40%   | -108    |  -658    |  -906    |  -540    | 1038    | -1578    |
| L1 long straddle      | SPY    | 10:00   |        6 | 50%   |   14.57 |  -180    |  -346.6  |    87.4  |  126.2  |   -38.8  |
| L1 long straddle      | SPY    | 11:30   |        6 | 67%   |   39.57 |   -56.27 |  -178.6  |   237.4  |   20.2  |   217.2  |
| L1 long straddle      | SPY    | 13:00   |        6 | 67%   |   22.57 |   -45.93 |  -140.6  |   135.4  |   81.2  |    54.2  |
| L1 long straddle      | SPY    | 14:30   |        5 | 40%   |  -18.6  |   -66.2  |   -91.6  |   -93    |   63.8  |  -156.8  |
| T1 trend spread 15d   | SPXW   | 10:00   |        6 | 83%   | -153.67 |  -850    | -1902    |  -922    |  576    | -1498    |
| T1 trend spread 15d   | SPXW   | 11:30   |        6 | 83%   |   36.16 |  -209.71 |  -598.01 |   216.99 |  426    |  -209.01 |
| T1 trend spread 15d   | SPXW   | 13:00   |        6 | 67%   | -330.17 |  -804.84 | -1608.01 | -1981.03 | -732.02 | -1249.01 |
| T1 trend spread 15d   | SPXW   | 14:30   |        5 | 100%  |  109    |    87    |    57    |   545    |  164    |   381    |
| T1 trend spread 15d   | SPY    | 10:00   |        6 | 83%   |  -11.3  |   -77.64 |  -180.3  |   -67.8  |   68.1  |  -135.9  |
| T1 trend spread 15d   | SPY    | 11:30   |        6 | 100%  |   16.03 |    13.37 |     9.7  |    96.2  |   43.1  |    53.1  |
| T1 trend spread 15d   | SPY    | 13:00   |        6 | 67%   |  -15.8  |   -45.8  |   -77.3  |   -94.8  |  -47.9  |   -46.9  |
| T1 trend spread 15d   | SPY    | 14:30   |        5 | 100%  |   10.5  |     7.7  |     3.7  |    52.5  |   13.4  |    39.1  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             345 |                     462 |            -199 |              -5231 |                  -497 |
| 2026-11-11 |              858 |             648 |                    -245 |             807 |                257 |                   588 |
| 2026-11-12 |             1649 |              25 |                    -302 |           -2454 |               1332 |                 -1946 |
| 2026-11-13 |             2341 |             944 |                     383 |            1612 |              -3783 |                   811 |
| 2026-11-16 |             2661 |             808 |                     808 |           -3216 |               7126 |                 -1686 |
