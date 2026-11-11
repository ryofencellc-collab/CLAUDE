# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.94 (official close), 21 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.69 (official close), 21 trades
- 2026-11-10 SPXW: 434 snapshots, settle 7520.93 (official close), 21 trades
- 2026-11-10 SPY: 427 snapshots, settle 749.92 (official close), 21 trades
- 2026-11-11 SPXW: 270 snapshots, settle 7644.29 (official close), 16 trades
- 2026-11-11 SPY: 270 snapshots, settle 762.19 (official close), 16 trades

Trading days scored: **3** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |    low90 |    worst |    total |      h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|---------:|--------:|---------:|
| B1 OR breakout        | SPXW   | -       |        3 | 67%   |  753.67 |  -363    | -1023    |  2261    | 2327    |   -66    |
| B1 OR breakout        | SPY    | -       |        3 | 33%   |   22.7  |  -104.63 |  -107.3  |    68.1  |  274.7  |  -206.6  |
| I1 condor 10d         | SPXW   | 10:00   |        3 | 67%   | -225.67 |  -725.33 | -1215    |  -677    |  254    |  -931    |
| I1 condor 10d         | SPXW   | 11:30   |        3 | 67%   |   44.33 |  -125.33 |  -290    |   133    |  204    |   -71    |
| I1 condor 10d         | SPXW   | 13:00   |        3 | 67%   |  -42.01 |  -214.68 |  -379.02 |  -126.02 |  139    |  -265.02 |
| I1 condor 10d         | SPXW   | 14:30   |        2 | 100%  |  114    |   nan    |    89    |   228    |   89    |   139    |
| I1 condor 10d         | SPY    | 10:00   |        3 | 67%   |  -13.6  |   -55.6  |   -96.6  |   -40.8  |   29.4  |   -70.2  |
| I1 condor 10d         | SPY    | 11:30   |        3 | 67%   |    9.4  |     0.73 |    -6.6  |    28.2  |   15.4  |    12.8  |
| I1 condor 10d         | SPY    | 13:00   |        3 | 100%  |   15.07 |    11.73 |    10.4  |    45.2  |   10.4  |    34.8  |
| I1 condor 10d         | SPY    | 14:30   |        2 | 100%  |   11.9  |   nan    |     8.4  |    23.8  |    8.4  |    15.4  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        3 | 33%   | -110    |  -318.67 |  -342    |  -330    | -342    |    12    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        3 | 33%   | -116.67 |  -320.33 |  -392    |  -350    | -392    |    42    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        3 | 33%   | -113.33 |  -238.67 |  -262    |  -340    | -192    |  -148    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        2 | 50%   |   -4    |   nan    |  -147    |    -8    | -147    |   139    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        3 | 33%   |  -19.33 |   -45.2  |   -51.2  |   -58    |  -51.2  |    -6.8  |
| I2 condor 10d stop 2x | SPY    | 11:30   |        3 | 33%   |  -10.33 |   -26.2  |   -28.2  |   -31    |  -28.2  |    -2.8  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        3 | 67%   |    5.53 |    -7.33 |   -18.2  |    16.6  |  -18.2  |    34.8  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        2 | 50%   |  -11.4  |   nan    |   -38.2  |   -22.8  |  -38.2  |    15.4  |
| I3 condor 20d         | SPXW   | 10:00   |        3 | 33%   | -727.33 | -1580.66 | -1946    | -2181.99 | -849.99 | -1332    |
| I3 condor 20d         | SPXW   | 11:30   |        3 | 67%   | -177.33 |  -848.67 | -1515    |  -532    |  484    | -1016    |
| I3 condor 20d         | SPXW   | 13:00   |        3 | 67%   | -303.67 |  -929.68 | -1554.02 |  -911.02 |  319    | -1230.02 |
| I3 condor 20d         | SPXW   | 14:30   |        2 | 100%  |  199.99 |   nan    |   189    |   399.98 |  189    |   210.98 |
| I3 condor 20d         | SPY    | 10:00   |        3 | 33%   |  -61.6  |  -164.93 |  -243.6  |  -184.8  |   -7.6  |  -177.2  |
| I3 condor 20d         | SPY    | 11:30   |        3 | 67%   |    6.73 |   -39.6  |   -84.6  |    20.2  |   50.4  |   -30.2  |
| I3 condor 20d         | SPY    | 13:00   |        3 | 67%   |  -18.27 |   -77.27 |  -131.6  |   -54.8  |   45.4  |  -100.2  |
| I3 condor 20d         | SPY    | 14:30   |        2 | 100%  |   34.4  |   nan    |    27.4  |    68.8  |   27.4  |    41.4  |
| L1 long straddle      | SPXW   | 10:00   |        3 | 67%   | 1083.67 | -1302.67 | -3676    |  3251    | 3444    |  -193    |
| L1 long straddle      | SPXW   | 11:30   |        3 | 67%   |  728.67 |  -713    | -2066    |  2186    | 2259    |   -73    |
| L1 long straddle      | SPXW   | 13:00   |        3 | 67%   |  443.67 |  -126.67 |  -617    |  1331    |  854    |   477    |
| L1 long straddle      | SPXW   | 14:30   |        2 | 50%   |  519    |   nan    |   -86    |  1038    | 1124    |   -86    |
| L1 long straddle      | SPY    | 10:00   |        3 | 67%   |  110.07 |  -138.6  |  -346.6  |   330.2  |  399.4  |   -69.2  |
| L1 long straddle      | SPY    | 11:30   |        3 | 67%   |   72.4  |   -56.27 |  -178.6  |   217.2  |  188.4  |    28.8  |
| L1 long straddle      | SPY    | 13:00   |        3 | 67%   |   28.73 |   -22.27 |   -55.6  |    86.2  |   97.4  |   -11.2  |
| L1 long straddle      | SPY    | 14:30   |        2 | 50%   |   31.9  |   nan    |   -16.6  |    63.8  |   80.4  |   -16.6  |
| T1 trend spread 15d   | SPXW   | 10:00   |        3 | 67%   | -617.67 | -1432.33 | -2242    | -1853    |  202    | -2055    |
| T1 trend spread 15d   | SPXW   | 11:30   |        3 | 100%  |  142    |   120.33 |   107    |   426    |  147    |   279    |
| T1 trend spread 15d   | SPXW   | 13:00   |        3 | 67%   | -244.01 |  -595.01 |  -941.02 |  -732.02 |  112    |  -844.02 |
| T1 trend spread 15d   | SPXW   | 14:30   |        2 | 100%  |   82    |   nan    |    57    |   164    |   57    |   107    |
| T1 trend spread 15d   | SPY    | 10:00   |        3 | 67%   |  -50.3  |  -125.97 |  -201.3  |  -150.9  |   25.7  |  -176.6  |
| T1 trend spread 15d   | SPY    | 11:30   |        3 | 100%  |   14.37 |    12.03 |     9.7  |    43.1  |   16.7  |    26.4  |
| T1 trend spread 15d   | SPY    | 13:00   |        3 | 67%   |  -15.97 |   -44.97 |   -73.3  |   -47.9  |   11.7  |   -59.6  |
| T1 trend spread 15d   | SPY    | 14:30   |        2 | 100%  |    6.7  |   nan    |     3.7  |    13.4  |    3.7  |     9.7  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             345 |                     462 |            -199 |              -5231 |                  -497 |
| 2026-11-11 |              858 |           -1480 |                    -376 |           -3434 |               5288 |                 -2216 |
