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

Trading days scored: **6** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |      h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|--------:|---------:|
| B1 OR breakout        | SPXW   | -       |        6 | 83%   | 1375.33 |   507    | -1023    |  8252    | 2261    |  5991    |
| B1 OR breakout        | SPY    | -       |        6 | 67%   |  121.2  |     7.53 |  -107.3  |   727.2  |   68.1  |   659.1  |
| I1 condor 10d         | SPXW   | 10:00   |        6 | 100%  |  253.17 |   235.67 |   214    |  1519    |  752    |   767    |
| I1 condor 10d         | SPXW   | 11:30   |        6 | 100%  |  209    |   182.33 |   139    |  1254    |  562    |   692    |
| I1 condor 10d         | SPXW   | 13:00   |        6 | 67%   |  -52.34 |  -276.18 |  -606.01 |  -314.03 | -126.02 |  -188.01 |
| I1 condor 10d         | SPXW   | 14:30   |        6 | 100%  |  137.33 |   115.67 |    89    |   824    |  347    |   477    |
| I1 condor 10d         | SPY    | 10:00   |        6 | 100%  |   25.4  |    23.57 |    22.4  |   152.4  |   78.2  |    74.2  |
| I1 condor 10d         | SPY    | 11:30   |        6 | 100%  |   19.9  |    16.57 |    12.4  |   119.4  |   47.2  |    72.2  |
| I1 condor 10d         | SPY    | 13:00   |        6 | 100%  |   16.23 |    13.4  |    10.4  |    97.4  |   45.2  |    52.2  |
| I1 condor 10d         | SPY    | 14:30   |        6 | 100%  |   12.57 |    10.9  |     8.4  |    75.4  |   36.2  |    39.2  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        6 | 17%   | -221    |  -339.5  |  -382    | -1326    | -330    |  -996    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        6 | 50%   |  -31.5  |  -212.67 |  -392    |  -189    | -350    |   161    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        6 | 33%   |  -96.67 |  -226.17 |  -262    |  -580    | -340    |  -240    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        6 | 83%   |   98    |     8.5  |  -147    |   588    |  111    |   477    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        6 | 33%   |  -16.33 |   -37.37 |   -51.2  |   -98    |  -58    |   -40    |
| I2 condor 10d stop 2x | SPY    | 11:30   |        6 | 50%   |   -4.07 |   -21.93 |   -37.2  |   -24.4  |  -31    |     6.6  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        6 | 50%   |   -2.57 |   -17.27 |   -31.2  |   -15.4  |   16.6  |   -32    |
| I2 condor 10d stop 2x | SPY    | 14:30   |        6 | 67%   |   -1.97 |   -17.17 |   -38.2  |   -11.8  |  -10.4  |    -1.4  |
| I3 condor 20d         | SPXW   | 10:00   |        6 | 50%   | -208.83 |  -859.88 | -1841    | -1252.98 | -619.98 |  -633    |
| I3 condor 20d         | SPXW   | 11:30   |        6 | 50%   | -190.67 |  -748.68 | -1246.01 | -1144.02 | 1397    | -2541.02 |
| I3 condor 20d         | SPXW   | 13:00   |        6 | 50%   | -438.34 | -1093.52 | -1881.01 | -2630.05 | -911.02 | -1719.03 |
| I3 condor 20d         | SPXW   | 14:30   |        6 | 100%  |  285.16 |   203.59 |   108.99 |  1710.97 |  778.98 |   931.99 |
| I3 condor 20d         | SPY    | 10:00   |        6 | 50%   |   -9.93 |   -94.27 |  -233.6  |   -59.6  |   34.2  |   -93.8  |
| I3 condor 20d         | SPY    | 11:30   |        6 | 67%   |   15.4  |   -10.43 |   -38.6  |    92.4  |  139.2  |   -46.8  |
| I3 condor 20d         | SPY    | 13:00   |        6 | 67%   |  -16.43 |   -78.77 |  -148.6  |   -98.6  |  -54.8  |   -43.8  |
| I3 condor 20d         | SPY    | 14:30   |        6 | 100%  |   41.07 |    35.07 |    27.4  |   246.4  |  101.2  |   145.2  |
| L1 long straddle      | SPXW   | 10:00   |        6 | 50%   |  326.5  | -1810.17 | -3676    |  1959    | 1227    |   732    |
| L1 long straddle      | SPXW   | 11:30   |        6 | 67%   |  684    |  -396.83 | -2066    |  4104    |  252    |  3852    |
| L1 long straddle      | SPXW   | 13:00   |        6 | 67%   |  574    |  -214.33 | -1311    |  3444    | 1552    |  1892    |
| L1 long straddle      | SPXW   | 14:30   |        6 | 33%   | -176    |  -606    |  -906    | -1056    |  232    | -1288    |
| L1 long straddle      | SPY    | 10:00   |        6 | 50%   |   22.4  |  -179.93 |  -346.6  |   134.4  |  126.2  |     8.2  |
| L1 long straddle      | SPY    | 11:30   |        6 | 67%   |   48.9  |   -54.43 |  -178.6  |   293.4  |   20.2  |   273.2  |
| L1 long straddle      | SPY    | 13:00   |        6 | 67%   |   33.9  |   -36.6  |  -140.6  |   203.4  |   81.2  |   122.2  |
| L1 long straddle      | SPY    | 14:30   |        6 | 33%   |  -19.6  |   -57.93 |   -91.6  |  -117.6  |  -18.8  |   -98.8  |
| T1 trend spread 15d   | SPXW   | 10:00   |        6 | 83%   | -189    |  -956.01 | -2114.02 | -1134.02 |  576    | -1710.02 |
| T1 trend spread 15d   | SPXW   | 11:30   |        6 | 83%   |   36.16 |  -209.71 |  -598.01 |   216.99 |  426    |  -209.01 |
| T1 trend spread 15d   | SPXW   | 13:00   |        6 | 67%   | -330.17 |  -804.84 | -1608.01 | -1981.03 | -732.02 | -1249.01 |
| T1 trend spread 15d   | SPXW   | 14:30   |        6 | 100%  |  116.17 |    94.5  |    57    |   697    |  306    |   391    |
| T1 trend spread 15d   | SPY    | 10:00   |        6 | 83%   |  -10.97 |   -76.64 |  -178.3  |   -65.8  |   68.1  |  -133.9  |
| T1 trend spread 15d   | SPY    | 11:30   |        6 | 100%  |   16.03 |    13.37 |     9.7  |    96.2  |   43.1  |    53.1  |
| T1 trend spread 15d   | SPY    | 13:00   |        6 | 67%   |  -15.8  |   -45.8  |   -77.3  |   -94.8  |  -47.9  |   -46.9  |
| T1 trend spread 15d   | SPY    | 14:30   |        6 | 100%  |   11.2  |     8.53 |     3.7  |    67.2  |   27.1  |    40.1  |

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
