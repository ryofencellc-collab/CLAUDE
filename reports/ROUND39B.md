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

Trading days scored: **4** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |       h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|---------:|---------:|
| B1 OR breakout        | SPXW   | -       |        4 | 75%   |  929.5  |   -33    | -1023    |  3718    |  1304    |  2414    |
| B1 OR breakout        | SPY    | -       |        4 | 50%   |   64.95 |  -101.3  |  -107.3  |   259.8  |   167.4  |    92.4  |
| I1 condor 10d         | SPXW   | 10:00   |        4 | 100%  |  250.25 |   231.5  |   214    |  1001    |   538    |   463    |
| I1 condor 10d         | SPXW   | 11:30   |        4 | 100%  |  187.75 |   159    |   139    |   751    |   423    |   328    |
| I1 condor 10d         | SPXW   | 13:00   |        4 | 50%   | -183.01 |  -435.77 |  -606.01 |  -732.03 |  -240.02 |  -492.01 |
| I1 condor 10d         | SPXW   | 14:30   |        4 | 100%  |  117.75 |   104    |    89    |   471    |   228    |   243    |
| I1 condor 10d         | SPY    | 10:00   |        4 | 100%  |   25.15 |    22.4  |    22.4  |   100.6  |    55.8  |    44.8  |
| I1 condor 10d         | SPY    | 11:30   |        4 | 100%  |   17.15 |    14.15 |    12.4  |    68.6  |    34.8  |    33.8  |
| I1 condor 10d         | SPY    | 13:00   |        4 | 100%  |   14.4  |    11.4  |    10.4  |    57.6  |    30.8  |    26.8  |
| I1 condor 10d         | SPY    | 14:30   |        4 | 100%  |   12.15 |    10.4  |     8.4  |    48.6  |    23.8  |    24.8  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        4 | 25%   | -178    |  -354.5  |  -382    |  -712    |   -58    |  -654    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        4 | 50%   |  -40.25 |  -246.75 |  -392    |  -161    |  -173    |    12    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        4 | 25%   | -138    |  -237    |  -262    |  -552    |  -454    |   -98    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        4 | 75%   |   58.75 |   -14    |  -147    |   235    |    -8    |   243    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        4 | 25%   |  -22.55 |   -42.2  |   -51.2  |   -90.2  |   -24.8  |   -65.4  |
| I2 condor 10d stop 2x | SPY    | 11:30   |        4 | 50%   |   -2.4  |   -23.7  |   -28.2  |    -9.6  |    -8.8  |    -0.8  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        4 | 50%   |   -1.4  |   -19.2  |   -22.2  |    -5.6  |     2.2  |    -7.8  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        4 | 75%   |    0.5  |   -12.9  |   -38.2  |     2    |   -22.8  |    24.8  |
| I3 condor 20d         | SPXW   | 10:00   |        4 | 50%   |    2.25 |  -500.49 |  -849.99 |     9.02 |  -235.99 |   245.01 |
| I3 condor 20d         | SPXW   | 11:30   |        4 | 75%   |   37.75 |  -416    | -1246.01 |   150.99 |   983    |  -832.01 |
| I3 condor 20d         | SPXW   | 13:00   |        4 | 50%   | -698.01 | -1635.77 | -1881.01 | -2792.03 | -1235.02 | -1557.01 |
| I3 condor 20d         | SPXW   | 14:30   |        4 | 100%  |  221.99 |   149    |   108.99 |   887.97 |   399.98 |   487.99 |
| I3 condor 20d         | SPY    | 10:00   |        4 | 50%   |   26.9  |   -11.85 |   -24.6  |   107.6  |    58.8  |    48.8  |
| I3 condor 20d         | SPY    | 11:30   |        4 | 75%   |   26.9  |     1.4  |   -31.6  |   107.6  |   104.8  |     2.8  |
| I3 condor 20d         | SPY    | 13:00   |        4 | 50%   |  -50.85 |  -135.85 |  -148.6  |  -203.4  |   -86.2  |  -117.2  |
| I3 condor 20d         | SPY    | 14:30   |        4 | 100%  |   35.65 |    30.9  |    27.4  |   142.6  |    68.8  |    73.8  |
| L1 long straddle      | SPXW   | 10:00   |        4 | 50%   | -504.75 | -3353.5  | -3676    | -2019    |  -232    | -1787    |
| L1 long straddle      | SPXW   | 11:30   |        4 | 75%   |  617.75 |  -994.75 | -2066    |  2471    |   193    |  2278    |
| L1 long straddle      | SPXW   | 13:00   |        4 | 75%   |  930.25 |   229    |  -396    |  3721    |  1948    |  1773    |
| L1 long straddle      | SPXW   | 14:30   |        4 | 50%   |   91.5  |  -446    |  -806    |   366    |  1038    |  -672    |
| L1 long straddle      | SPY    | 10:00   |        4 | 50%   |  -44.6  |  -315.1  |  -346.6  |  -178.4  |    52.8  |  -231.2  |
| L1 long straddle      | SPY    | 11:30   |        4 | 75%   |   49.4  |   -84.1  |  -178.6  |   197.6  |     9.8  |   187.8  |
| L1 long straddle      | SPY    | 13:00   |        4 | 75%   |   61.65 |    -8.1  |   -60.6  |   246.6  |   141.8  |   104.8  |
| L1 long straddle      | SPY    | 14:30   |        4 | 50%   |   -0.35 |   -49.6  |   -82.6  |    -1.4  |    63.8  |   -65.2  |
| T1 trend spread 15d   | SPXW   | 10:00   |        4 | 100%  |  190.75 |   187    |   187    |   763    |   389    |   374    |
| T1 trend spread 15d   | SPXW   | 11:30   |        4 | 75%   |  -43    |  -245.5  |  -598.01 |  -172.01 |   319    |  -491.01 |
| T1 trend spread 15d   | SPXW   | 13:00   |        4 | 50%   | -585.01 | -1181.76 | -1608.01 | -2340.03 |  -829.02 | -1511.01 |
| T1 trend spread 15d   | SPXW   | 14:30   |        4 | 100%  |  103.25 |    82    |    57    |   413    |   164    |   249    |
| T1 trend spread 15d   | SPY    | 10:00   |        4 | 100%  |   21.45 |    17.7  |    17.7  |    85.8  |    50.4  |    35.4  |
| T1 trend spread 15d   | SPY    | 11:30   |        4 | 100%  |   14.2  |    11.45 |     9.7  |    56.8  |    33.4  |    23.4  |
| T1 trend spread 15d   | SPY    | 13:00   |        4 | 50%   |  -31.3  |   -74.3  |   -77.3  |  -125.2  |   -61.6  |   -63.6  |
| T1 trend spread 15d   | SPY    | 14:30   |        4 | 100%  |    9.7  |     6.7  |     3.7  |    38.8  |    13.4  |    25.4  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             345 |                     462 |            -199 |              -5231 |                  -497 |
| 2026-11-11 |              858 |             648 |                    -245 |             807 |                257 |                   588 |
| 2026-11-12 |             1649 |              25 |                    -302 |           -2454 |               1332 |                 -1946 |
