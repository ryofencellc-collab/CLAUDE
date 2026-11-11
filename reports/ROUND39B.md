# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.94 (official close), 21 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.69 (official close), 21 trades
- 2026-11-10 SPXW: 434 snapshots, settle 7520.93 (official close), 21 trades
- 2026-11-10 SPY: 427 snapshots, settle 749.92 (official close), 21 trades
- 2026-11-11 SPXW: 439 snapshots, settle 7619.38 (official close), 21 trades
- 2026-11-11 SPY: 439 snapshots, settle 759.84 (official close), 21 trades

Trading days scored: **3** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |    low90 |    worst |   total |      h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|--------:|--------:|---------:|
| B1 OR breakout        | SPXW   | -       |        3 | 67%   |  753.67 |  -363    | -1023    | 2261    | 2327    |   -66    |
| B1 OR breakout        | SPY    | -       |        3 | 33%   |   22.7  |  -104.63 |  -107.3  |   68.1  |  274.7  |  -206.6  |
| I1 condor 10d         | SPXW   | 10:00   |        3 | 100%  |  250.67 |   227.33 |   214    |  752    |  254    |   498    |
| I1 condor 10d         | SPXW   | 11:30   |        3 | 100%  |  187.33 |   160.67 |   139    |  562    |  204    |   358    |
| I1 condor 10d         | SPXW   | 13:00   |        3 | 67%   |  -42.01 |  -214.68 |  -379.02 | -126.02 |  139    |  -265.02 |
| I1 condor 10d         | SPXW   | 14:30   |        3 | 100%  |  115.67 |    99    |    89    |  347    |   89    |   258    |
| I1 condor 10d         | SPY    | 10:00   |        3 | 100%  |   26.07 |    23.73 |    22.4  |   78.2  |   29.4  |    48.8  |
| I1 condor 10d         | SPY    | 11:30   |        3 | 100%  |   15.73 |    13.4  |    12.4  |   47.2  |   15.4  |    31.8  |
| I1 condor 10d         | SPY    | 13:00   |        3 | 100%  |   15.07 |    11.73 |    10.4  |   45.2  |   10.4  |    34.8  |
| I1 condor 10d         | SPY    | 14:30   |        3 | 100%  |   12.07 |     9.73 |     8.4  |   36.2  |    8.4  |    27.8  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        3 | 33%   | -110    |  -318.67 |  -342    | -330    | -342    |    12    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        3 | 33%   | -116.67 |  -320.33 |  -392    | -350    | -392    |    42    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        3 | 33%   | -113.33 |  -238.67 |  -262    | -340    | -192    |  -148    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        3 | 67%   |   37    |   -58.33 |  -147    |  111    | -147    |   258    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        3 | 33%   |  -19.33 |   -45.2  |   -51.2  |  -58    |  -51.2  |    -6.8  |
| I2 condor 10d stop 2x | SPY    | 11:30   |        3 | 33%   |  -10.33 |   -26.2  |   -28.2  |  -31    |  -28.2  |    -2.8  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        3 | 67%   |    5.53 |    -7.33 |   -18.2  |   16.6  |  -18.2  |    34.8  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        3 | 67%   |   -3.47 |   -21.33 |   -38.2  |  -10.4  |  -38.2  |    27.8  |
| I3 condor 20d         | SPXW   | 10:00   |        3 | 33%   | -206.66 |  -694.66 |  -849.99 | -619.98 | -849.99 |   230.01 |
| I3 condor 20d         | SPXW   | 11:30   |        3 | 100%  |  465.67 |   437.33 |   414    | 1397    |  484    |   913    |
| I3 condor 20d         | SPXW   | 13:00   |        3 | 67%   | -303.67 |  -929.68 | -1554.02 | -911.02 |  319    | -1230.02 |
| I3 condor 20d         | SPXW   | 14:30   |        3 | 100%  |  259.66 |   196.33 |   189    |  778.98 |  189    |   589.98 |
| I3 condor 20d         | SPY    | 10:00   |        3 | 33%   |   10.4  |   -20.93 |   -27.6  |   31.2  |   -7.6  |    38.8  |
| I3 condor 20d         | SPY    | 11:30   |        3 | 100%  |   46.4  |    39.73 |    34.4  |  139.2  |   50.4  |    88.8  |
| I3 condor 20d         | SPY    | 13:00   |        3 | 67%   |  -18.27 |   -77.27 |  -131.6  |  -54.8  |   45.4  |  -100.2  |
| I3 condor 20d         | SPY    | 14:30   |        3 | 100%  |   33.73 |    29.07 |    27.4  |  101.2  |   27.4  |    73.8  |
| L1 long straddle      | SPXW   | 10:00   |        3 | 67%   |  409    | -1964.33 | -3676    | 1227    | 3444    | -2217    |
| L1 long straddle      | SPXW   | 11:30   |        3 | 67%   |   84    | -1357.67 | -2066    |  252    | 2259    | -2007    |
| L1 long straddle      | SPXW   | 13:00   |        3 | 67%   |  517.33 |    20.67 |  -396    | 1552    |  854    |   698    |
| L1 long straddle      | SPXW   | 14:30   |        3 | 33%   |   77.33 |  -566    |  -806    |  232    | 1124    |  -892    |
| L1 long straddle      | SPY    | 10:00   |        3 | 67%   |   42.07 |  -206.6  |  -346.6  |  126.2  |  399.4  |  -273.2  |
| L1 long straddle      | SPY    | 11:30   |        3 | 67%   |    6.73 |  -115.6  |  -178.6  |   20.2  |  188.4  |  -168.2  |
| L1 long straddle      | SPY    | 13:00   |        3 | 67%   |   27.07 |   -25.6  |   -60.6  |   81.2  |   97.4  |   -16.2  |
| L1 long straddle      | SPY    | 14:30   |        3 | 33%   |   -6.27 |   -60.6  |   -82.6  |  -18.8  |   80.4  |   -99.2  |
| T1 trend spread 15d   | SPXW   | 10:00   |        3 | 100%  |  192    |   187    |   187    |  576    |  202    |   374    |
| T1 trend spread 15d   | SPXW   | 11:30   |        3 | 100%  |  142    |   120.33 |   107    |  426    |  147    |   279    |
| T1 trend spread 15d   | SPXW   | 13:00   |        3 | 67%   | -244.01 |  -595.01 |  -941.02 | -732.02 |  112    |  -844.02 |
| T1 trend spread 15d   | SPXW   | 14:30   |        3 | 100%  |  102    |    73.67 |    57    |  306    |   57    |   249    |
| T1 trend spread 15d   | SPY    | 10:00   |        3 | 100%  |   22.7  |    20.03 |    17.7  |   68.1  |   25.7  |    42.4  |
| T1 trend spread 15d   | SPY    | 11:30   |        3 | 100%  |   14.37 |    12.03 |     9.7  |   43.1  |   16.7  |    26.4  |
| T1 trend spread 15d   | SPY    | 13:00   |        3 | 67%   |  -15.97 |   -44.97 |   -73.3  |  -47.9  |   11.7  |   -59.6  |
| T1 trend spread 15d   | SPY    | 14:30   |        3 | 100%  |    9.03 |     5.7  |     3.7  |   27.1  |    3.7  |    23.4  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             345 |                     462 |            -199 |              -5231 |                  -497 |
| 2026-11-11 |              858 |             648 |                    -245 |             804 |                257 |                   588 |
