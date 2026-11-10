# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.94 (official close), 21 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.69 (official close), 21 trades
- 2026-11-10 SPXW: 434 snapshots, settle 7520.93 (official close), 21 trades
- 2026-11-10 SPY: 427 snapshots, settle 749.92 (official close), 21 trades

Trading days scored: **2** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |   low90 |    worst |    total |      h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|--------:|---------:|---------:|--------:|---------:|
| B1 OR breakout        | SPXW   | -       |        2 | 50%   |  652    |     nan | -1023    |  1304    | 2327    | -1023    |
| B1 OR breakout        | SPY    | -       |        2 | 50%   |   83.7  |     nan |  -107.3  |   167.4  |  274.7  |  -107.3  |
| I1 condor 10d         | SPXW   | 10:00   |        2 | 100%  |  269    |     nan |   254    |   538    |  254    |   284    |
| I1 condor 10d         | SPXW   | 11:30   |        2 | 100%  |  211.5  |     nan |   204    |   423    |  204    |   219    |
| I1 condor 10d         | SPXW   | 13:00   |        2 | 50%   | -120.01 |     nan |  -379.02 |  -240.02 |  139    |  -379.02 |
| I1 condor 10d         | SPXW   | 14:30   |        2 | 100%  |  114    |     nan |    89    |   228    |   89    |   139    |
| I1 condor 10d         | SPY    | 10:00   |        2 | 100%  |   27.9  |     nan |    26.4  |    55.8  |   29.4  |    26.4  |
| I1 condor 10d         | SPY    | 11:30   |        2 | 100%  |   17.4  |     nan |    15.4  |    34.8  |   15.4  |    19.4  |
| I1 condor 10d         | SPY    | 13:00   |        2 | 100%  |   15.4  |     nan |    10.4  |    30.8  |   10.4  |    20.4  |
| I1 condor 10d         | SPY    | 14:30   |        2 | 100%  |   11.9  |     nan |     8.4  |    23.8  |    8.4  |    15.4  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        2 | 50%   |  -29    |     nan |  -342    |   -58    | -342    |   284    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        2 | 50%   |  -86.5  |     nan |  -392    |  -173    | -392    |   219    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        2 | 0%    | -227    |     nan |  -262    |  -454    | -192    |  -262    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        2 | 50%   |   -4    |     nan |  -147    |    -8    | -147    |   139    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        2 | 50%   |  -12.4  |     nan |   -51.2  |   -24.8  |  -51.2  |    26.4  |
| I2 condor 10d stop 2x | SPY    | 11:30   |        2 | 50%   |   -4.4  |     nan |   -28.2  |    -8.8  |  -28.2  |    19.4  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        2 | 50%   |    1.1  |     nan |   -18.2  |     2.2  |  -18.2  |    20.4  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        2 | 50%   |  -11.4  |     nan |   -38.2  |   -22.8  |  -38.2  |    15.4  |
| I3 condor 20d         | SPXW   | 10:00   |        2 | 50%   | -118    |     nan |  -849.99 |  -235.99 | -849.99 |   614    |
| I3 condor 20d         | SPXW   | 11:30   |        2 | 100%  |  491.5  |     nan |   484    |   983    |  484    |   499    |
| I3 condor 20d         | SPXW   | 13:00   |        2 | 50%   | -617.51 |     nan | -1554.02 | -1235.02 |  319    | -1554.02 |
| I3 condor 20d         | SPXW   | 14:30   |        2 | 100%  |  199.99 |     nan |   189    |   399.98 |  189    |   210.98 |
| I3 condor 20d         | SPY    | 10:00   |        2 | 50%   |   29.4  |     nan |    -7.6  |    58.8  |   -7.6  |    66.4  |
| I3 condor 20d         | SPY    | 11:30   |        2 | 100%  |   52.4  |     nan |    50.4  |   104.8  |   50.4  |    54.4  |
| I3 condor 20d         | SPY    | 13:00   |        2 | 50%   |  -43.1  |     nan |  -131.6  |   -86.2  |   45.4  |  -131.6  |
| I3 condor 20d         | SPY    | 14:30   |        2 | 100%  |   34.4  |     nan |    27.4  |    68.8  |   27.4  |    41.4  |
| L1 long straddle      | SPXW   | 10:00   |        2 | 50%   | -116    |     nan | -3676    |  -232    | 3444    | -3676    |
| L1 long straddle      | SPXW   | 11:30   |        2 | 50%   |   96.5  |     nan | -2066    |   193    | 2259    | -2066    |
| L1 long straddle      | SPXW   | 13:00   |        2 | 100%  |  974    |     nan |   854    |  1948    |  854    |  1094    |
| L1 long straddle      | SPXW   | 14:30   |        2 | 50%   |  519    |     nan |   -86    |  1038    | 1124    |   -86    |
| L1 long straddle      | SPY    | 10:00   |        2 | 50%   |   26.4  |     nan |  -346.6  |    52.8  |  399.4  |  -346.6  |
| L1 long straddle      | SPY    | 11:30   |        2 | 50%   |    4.9  |     nan |  -178.6  |     9.8  |  188.4  |  -178.6  |
| L1 long straddle      | SPY    | 13:00   |        2 | 100%  |   70.9  |     nan |    44.4  |   141.8  |   97.4  |    44.4  |
| L1 long straddle      | SPY    | 14:30   |        2 | 50%   |   31.9  |     nan |   -16.6  |    63.8  |   80.4  |   -16.6  |
| T1 trend spread 15d   | SPXW   | 10:00   |        2 | 100%  |  194.5  |     nan |   187    |   389    |  202    |   187    |
| T1 trend spread 15d   | SPXW   | 11:30   |        2 | 100%  |  159.5  |     nan |   147    |   319    |  147    |   172    |
| T1 trend spread 15d   | SPXW   | 13:00   |        2 | 50%   | -414.51 |     nan |  -941.02 |  -829.02 |  112    |  -941.02 |
| T1 trend spread 15d   | SPXW   | 14:30   |        2 | 100%  |   82    |     nan |    57    |   164    |   57    |   107    |
| T1 trend spread 15d   | SPY    | 10:00   |        2 | 100%  |   25.2  |     nan |    24.7  |    50.4  |   25.7  |    24.7  |
| T1 trend spread 15d   | SPY    | 11:30   |        2 | 100%  |   16.7  |     nan |    16.7  |    33.4  |   16.7  |    16.7  |
| T1 trend spread 15d   | SPY    | 13:00   |        2 | 50%   |  -30.8  |     nan |   -73.3  |   -61.6  |   11.7  |   -73.3  |
| T1 trend spread 15d   | SPY    | 14:30   |        2 | 100%  |    6.7  |     nan |     3.7  |    13.4  |    3.7  |     9.7  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             345 |                     462 |            -199 |              -5231 |                  -497 |
