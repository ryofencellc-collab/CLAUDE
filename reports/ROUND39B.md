# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.94 (official close), 21 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.69 (official close), 21 trades
- 2026-11-10 SPXW: 265 snapshots, settle 7488.62 (official close), 16 trades
- 2026-11-10 SPY: 258 snapshots, settle 746.71 (official close), 16 trades

Trading days scored: **2** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |   mean |   low90 |    worst |   total |      h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|-------:|--------:|---------:|--------:|--------:|---------:|
| B1 OR breakout        | SPXW   | -       |        2 | 50%   |  652   |     nan | -1023    | 1304    | 2327    | -1023    |
| B1 OR breakout        | SPY    | -       |        2 | 50%   |   83.7 |     nan |  -107.3  |  167.4  |  274.7  |  -107.3  |
| I1 condor 10d         | SPXW   | 10:00   |        2 | 100%  |  269   |     nan |   254    |  538    |  254    |   284    |
| I1 condor 10d         | SPXW   | 11:30   |        2 | 100%  |  211.5 |     nan |   204    |  423    |  204    |   219    |
| I1 condor 10d         | SPXW   | 13:00   |        2 | 100%  |  176.5 |     nan |   139    |  353    |  139    |   214    |
| I1 condor 10d         | SPXW   | 14:30   |        1 | 100%  |   89   |     nan |    89    |   89    |  nan    |   nan    |
| I1 condor 10d         | SPY    | 10:00   |        2 | 100%  |   27.9 |     nan |    26.4  |   55.8  |   29.4  |    26.4  |
| I1 condor 10d         | SPY    | 11:30   |        2 | 100%  |   17.4 |     nan |    15.4  |   34.8  |   15.4  |    19.4  |
| I1 condor 10d         | SPY    | 13:00   |        2 | 100%  |   15.4 |     nan |    10.4  |   30.8  |   10.4  |    20.4  |
| I1 condor 10d         | SPY    | 14:30   |        1 | 100%  |    8.4 |     nan |     8.4  |    8.4  |  nan    |   nan    |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        2 | 50%   |  -29   |     nan |  -342    |  -58    | -342    |   284    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        2 | 50%   |  -86.5 |     nan |  -392    | -173    | -392    |   219    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        2 | 50%   |   11   |     nan |  -192    |   22    | -192    |   214    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        1 | 0%    | -147   |     nan |  -147    | -147    |  nan    |   nan    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        2 | 50%   |  -12.4 |     nan |   -51.2  |  -24.8  |  -51.2  |    26.4  |
| I2 condor 10d stop 2x | SPY    | 11:30   |        2 | 50%   |   -4.4 |     nan |   -28.2  |   -8.8  |  -28.2  |    19.4  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        2 | 50%   |    1.1 |     nan |   -18.2  |    2.2  |  -18.2  |    20.4  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        1 | 0%    |  -38.2 |     nan |   -38.2  |  -38.2  |  nan    |   nan    |
| I3 condor 20d         | SPXW   | 10:00   |        2 | 50%   | -118   |     nan |  -849.99 | -235.99 | -849.99 |   614    |
| I3 condor 20d         | SPXW   | 11:30   |        2 | 100%  |  491.5 |     nan |   484    |  983    |  484    |   499    |
| I3 condor 20d         | SPXW   | 13:00   |        2 | 100%  |  429   |     nan |   319    |  858    |  319    |   539    |
| I3 condor 20d         | SPXW   | 14:30   |        1 | 100%  |  189   |     nan |   189    |  189    |  nan    |   nan    |
| I3 condor 20d         | SPY    | 10:00   |        2 | 50%   |   29.4 |     nan |    -7.6  |   58.8  |   -7.6  |    66.4  |
| I3 condor 20d         | SPY    | 11:30   |        2 | 100%  |   52.4 |     nan |    50.4  |  104.8  |   50.4  |    54.4  |
| I3 condor 20d         | SPY    | 13:00   |        2 | 100%  |   52.9 |     nan |    45.4  |  105.8  |   45.4  |    60.4  |
| I3 condor 20d         | SPY    | 14:30   |        1 | 100%  |   27.4 |     nan |    27.4  |   27.4  |  nan    |   nan    |
| L1 long straddle      | SPXW   | 10:00   |        2 | 50%   |  708   |     nan | -2028.01 | 1415.99 | 3444    | -2028.01 |
| L1 long straddle      | SPXW   | 11:30   |        2 | 50%   |  315.5 |     nan | -1628.01 |  630.99 | 2259    | -1628.01 |
| L1 long straddle      | SPXW   | 13:00   |        2 | 50%   | -260   |     nan | -1373.99 | -519.99 |  854    | -1373.99 |
| L1 long straddle      | SPXW   | 14:30   |        1 | 100%  | 1124   |     nan |  1124    | 1124    |  nan    |   nan    |
| L1 long straddle      | SPY    | 10:00   |        2 | 50%   |   70.4 |     nan |  -258.6  |  140.8  |  399.4  |  -258.6  |
| L1 long straddle      | SPY    | 11:30   |        2 | 50%   |  -17.6 |     nan |  -223.6  |  -35.2  |  188.4  |  -223.6  |
| L1 long straddle      | SPY    | 13:00   |        2 | 50%   |  -60.6 |     nan |  -218.6  | -121.2  |   97.4  |  -218.6  |
| L1 long straddle      | SPY    | 14:30   |        1 | 100%  |   80.4 |     nan |    80.4  |   80.4  |  nan    |   nan    |
| T1 trend spread 15d   | SPXW   | 10:00   |        2 | 100%  |  194.5 |     nan |   187    |  389    |  202    |   187    |
| T1 trend spread 15d   | SPXW   | 11:30   |        2 | 100%  |  159.5 |     nan |   147    |  319    |  147    |   172    |
| T1 trend spread 15d   | SPXW   | 13:00   |        2 | 100%  |  132   |     nan |   112    |  264    |  112    |   152    |
| T1 trend spread 15d   | SPXW   | 14:30   |        1 | 100%  |   57   |     nan |    57    |   57    |  nan    |   nan    |
| T1 trend spread 15d   | SPY    | 10:00   |        2 | 100%  |   25.2 |     nan |    24.7  |   50.4  |   25.7  |    24.7  |
| T1 trend spread 15d   | SPY    | 11:30   |        2 | 100%  |   16.7 |     nan |    16.7  |   33.4  |   16.7  |    16.7  |
| T1 trend spread 15d   | SPY    | 13:00   |        2 | 100%  |   15.2 |     nan |    11.7  |   30.4  |   11.7  |    18.7  |
| T1 trend spread 15d   | SPY    | 14:30   |        1 | 100%  |    3.7 |     nan |     3.7  |    3.7  |  nan    |   nan    |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             783 |                     783 |            1833 |              -5731 |                   571 |
