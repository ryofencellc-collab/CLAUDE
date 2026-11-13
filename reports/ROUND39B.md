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
- 2026-11-13 SPY: 438 snapshots, settle 754.21 (official close), 21 trades

Trading days scored: **5** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |       h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|---------:|---------:|
| B1 OR breakout        | SPXW   | -       |        5 | 80%   | 1167    |   265    | -1023    |  5835    |  1304    |  4531    |
| B1 OR breakout        | SPY    | -       |        5 | 60%   |   96.7  |   -37.9  |  -107.3  |   483.5  |   167.4  |   316.1  |
| I1 condor 10d         | SPXW   | 10:00   |        5 | 100%  |  247    |   230    |   214    |  1235    |   538    |   697    |
| I1 condor 10d         | SPXW   | 11:30   |        5 | 100%  |  201    |   172    |   139    |  1005    |   423    |   582    |
| I1 condor 10d         | SPXW   | 13:00   |        5 | 60%   | -102.61 |  -350.21 |  -606.01 |  -513.03 |  -240.02 |  -273.01 |
| I1 condor 10d         | SPXW   | 14:30   |        5 | 100%  |  126    |   109    |    89    |   630    |   228    |   402    |
| I1 condor 10d         | SPY    | 10:00   |        5 | 100%  |   24.6  |    22.4  |    22.4  |   123    |    55.8  |    67.2  |
| I1 condor 10d         | SPY    | 11:30   |        5 | 100%  |   18.2  |    15.4  |    12.4  |    91    |    34.8  |    56.2  |
| I1 condor 10d         | SPY    | 13:00   |        5 | 100%  |   15.8  |    12.6  |    10.4  |    79    |    30.8  |    48.2  |
| I1 condor 10d         | SPY    | 14:30   |        5 | 100%  |   12    |    10.4  |     8.4  |    60    |    23.8  |    36.2  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        5 | 20%   | -195.8  |  -337    |  -382    |  -979    |   -58    |  -921    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        5 | 60%   |   18.6  |  -183.8  |  -392    |    93    |  -173    |   266    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        5 | 40%   |  -66.6  |  -214    |  -262    |  -333    |  -454    |   121    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        5 | 80%   |   78.8  |   -28.6  |  -147    |   394    |    -8    |   402    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        5 | 20%   |  -25.48 |   -41.8  |   -51.2  |  -127.4  |   -24.8  |  -102.6  |
| I2 condor 10d stop 2x | SPY    | 11:30   |        5 | 60%   |    2.56 |   -15.88 |   -28.2  |    12.8  |    -8.8  |    21.6  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        5 | 60%   |    3.16 |   -12.08 |   -22.2  |    15.8  |     2.2  |    13.6  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        5 | 80%   |    2.68 |   -17.36 |   -38.2  |    13.4  |   -22.8  |    36.2  |
| I3 condor 20d         | SPXW   | 10:00   |        5 | 60%   |  117.6  |  -370.79 |  -849.99 |   588.02 |  -235.99 |   824.01 |
| I3 condor 20d         | SPXW   | 11:30   |        5 | 60%   |   16.6  |  -548.16 | -1246.01 |    83    |   983    |  -900    |
| I3 condor 20d         | SPXW   | 13:00   |        5 | 60%   | -457.61 | -1273.21 | -1881.01 | -2288.03 | -1235.02 | -1053.01 |
| I3 condor 20d         | SPXW   | 14:30   |        5 | 100%  |  257.39 |   178.99 |   108.99 |  1286.97 |   399.98 |   886.99 |
| I3 condor 20d         | SPY    | 10:00   |        5 | 60%   |   34.8  |     0.4  |   -24.6  |   174    |    58.8  |   115.2  |
| I3 condor 20d         | SPY    | 11:30   |        5 | 80%   |   29.4  |     2.76 |   -31.6  |   147    |   104.8  |    42.2  |
| I3 condor 20d         | SPY    | 13:00   |        5 | 60%   |  -29    |  -102.4  |  -148.6  |  -145    |   -86.2  |   -58.8  |
| I3 condor 20d         | SPY    | 14:30   |        5 | 100%  |   38.4  |    32.8  |    27.4  |   192    |    68.8  |   123.2  |
| L1 long straddle      | SPXW   | 10:00   |        5 | 40%   | -582    | -2477    | -3676    | -2910    |  -232    | -2678    |
| L1 long straddle      | SPXW   | 11:30   |        5 | 60%   |  448    |  -793.15 | -2066    |  2240    |   193    |  2047    |
| L1 long straddle      | SPXW   | 13:00   |        5 | 60%   |  482    |  -445    | -1311    |  2410    |  1948    |   462    |
| L1 long straddle      | SPXW   | 14:30   |        5 | 40%   | -108    |  -658    |  -906    |  -540    |  1038    | -1578    |
| L1 long straddle      | SPY    | 10:00   |        5 | 40%   |  -59.6  |  -247.4  |  -346.6  |  -298    |    52.8  |  -350.8  |
| L1 long straddle      | SPY    | 11:30   |        5 | 60%   |   21    |   -85.8  |  -178.6  |   105    |     9.8  |    95.2  |
| L1 long straddle      | SPY    | 13:00   |        5 | 60%   |   21.2  |   -61    |  -140.6  |   106    |   141.8  |   -35.8  |
| L1 long straddle      | SPY    | 14:30   |        5 | 40%   |  -18.6  |   -66.2  |   -91.6  |   -93    |    63.8  |  -156.8  |
| T1 trend spread 15d   | SPXW   | 10:00   |        5 | 100%  |  196    |   187    |   187    |   980    |   389    |   591    |
| T1 trend spread 15d   | SPXW   | 11:30   |        5 | 80%   |    6    |  -278.01 |  -598.01 |    29.99 |   319    |  -289.01 |
| T1 trend spread 15d   | SPXW   | 13:00   |        5 | 60%   | -430.61 |  -982.21 | -1608.01 | -2153.03 |  -829.02 | -1324.01 |
| T1 trend spread 15d   | SPXW   | 14:30   |        5 | 100%  |  109    |    87    |    57    |   545    |   164    |   381    |
| T1 trend spread 15d   | SPY    | 10:00   |        5 | 100%  |   22.5  |    19.3  |    17.7  |   112.5  |    50.4  |    62.1  |
| T1 trend spread 15d   | SPY    | 11:30   |        5 | 100%  |   14.7  |    12.5  |     9.7  |    73.5  |    33.4  |    40.1  |
| T1 trend spread 15d   | SPY    | 13:00   |        5 | 60%   |  -21.9  |   -57.1  |   -77.3  |  -109.5  |   -61.6  |   -47.9  |
| T1 trend spread 15d   | SPY    | 14:30   |        5 | 100%  |   10.5  |     7.7  |     3.7  |    52.5  |    13.4  |    39.1  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             345 |                     462 |            -199 |              -5231 |                  -497 |
| 2026-11-11 |              858 |             648 |                    -245 |             807 |                257 |                   588 |
| 2026-11-12 |             1649 |              25 |                    -302 |           -2454 |               1332 |                 -1946 |
| 2026-11-13 |             2341 |             944 |                     383 |            1628 |              -3783 |                   811 |
