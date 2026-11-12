# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.94 (official close), 21 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.69 (official close), 21 trades
- 2026-11-10 SPXW: 434 snapshots, settle 7520.93 (official close), 21 trades
- 2026-11-10 SPY: 427 snapshots, settle 749.92 (official close), 21 trades
- 2026-11-11 SPXW: 439 snapshots, settle 7619.38 (official close), 21 trades
- 2026-11-11 SPY: 439 snapshots, settle 759.81 (official close), 21 trades
- 2026-11-12 SPXW: 270 snapshots, settle 7626.34 (official close), 16 trades
- 2026-11-12 SPY: 270 snapshots, settle 760.39 (official close), 16 trades

Trading days scored: **4** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |    low90 |    worst |   total |       h1 |       h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|---------:|---------:|--------:|---------:|---------:|
| B1 OR breakout        | SPXW   | -       |        4 | 75%   |  929.5  |   -33    | -1023    | 3718    |  1304    |  2414    |
| B1 OR breakout        | SPY    | -       |        4 | 50%   |   64.95 |  -101.3  |  -107.3  |  259.8  |   167.4  |    92.4  |
| I1 condor 10d         | SPXW   | 10:00   |        4 | 100%  |  250.25 |   231.5  |   214    | 1001    |   538    |   463    |
| I1 condor 10d         | SPXW   | 11:30   |        4 | 100%  |  187.75 |   159    |   139    |  751    |   423    |   328    |
| I1 condor 10d         | SPXW   | 13:00   |        4 | 75%   |    7    |  -132.51 |  -379.02 |   27.98 |  -240.02 |   268    |
| I1 condor 10d         | SPXW   | 14:30   |        3 | 100%  |  115.67 |    99    |    89    |  347    |    89    |   258    |
| I1 condor 10d         | SPY    | 10:00   |        4 | 100%  |   25.15 |    22.4  |    22.4  |  100.6  |    55.8  |    44.8  |
| I1 condor 10d         | SPY    | 11:30   |        4 | 100%  |   17.15 |    14.15 |    12.4  |   68.6  |    34.8  |    33.8  |
| I1 condor 10d         | SPY    | 13:00   |        4 | 100%  |   14.4  |    11.4  |    10.4  |   57.6  |    30.8  |    26.8  |
| I1 condor 10d         | SPY    | 14:30   |        3 | 100%  |   12.07 |     9.73 |     8.4  |   36.2  |     8.4  |    27.8  |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        4 | 25%   | -178    |  -354.5  |  -382    | -712    |   -58    |  -654    |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        4 | 50%   |  -40.25 |  -246.75 |  -392    | -161    |  -173    |    12    |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        4 | 50%   |  -46.5  |  -209.5  |  -262    | -186    |  -454    |   268    |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        3 | 67%   |   37    |   -58.33 |  -147    |  111    |  -147    |   258    |
| I2 condor 10d stop 2x | SPY    | 10:00   |        4 | 25%   |  -22.55 |   -42.2  |   -51.2  |  -90.2  |   -24.8  |   -65.4  |
| I2 condor 10d stop 2x | SPY    | 11:30   |        4 | 50%   |   -2.4  |   -23.7  |   -28.2  |   -9.6  |    -8.8  |    -0.8  |
| I2 condor 10d stop 2x | SPY    | 13:00   |        4 | 75%   |    7.25 |    -2.9  |   -18.2  |   29    |     2.2  |    26.8  |
| I2 condor 10d stop 2x | SPY    | 14:30   |        3 | 67%   |   -3.47 |   -21.33 |   -38.2  |  -10.4  |   -38.2  |    27.8  |
| I3 condor 20d         | SPXW   | 10:00   |        4 | 50%   |    2.25 |  -500.49 |  -849.99 |    9.02 |  -235.99 |   245.01 |
| I3 condor 20d         | SPXW   | 11:30   |        4 | 100%  |  477.75 |   439    |   414    | 1911    |   983    |   928    |
| I3 condor 20d         | SPXW   | 13:00   |        4 | 75%   | -133    |  -617.51 | -1554.02 | -532.02 | -1235.02 |   703    |
| I3 condor 20d         | SPXW   | 14:30   |        3 | 100%  |  259.66 |   196.33 |   189    |  778.98 |   189    |   589.98 |
| I3 condor 20d         | SPY    | 10:00   |        4 | 50%   |   26.9  |   -11.85 |   -24.6  |  107.6  |    58.8  |    48.8  |
| I3 condor 20d         | SPY    | 11:30   |        4 | 100%  |   48.9  |    39.9  |    34.4  |  195.6  |   104.8  |    90.8  |
| I3 condor 20d         | SPY    | 13:00   |        4 | 75%   |   -3.85 |   -50.1  |  -131.6  |  -15.4  |   -86.2  |    70.8  |
| I3 condor 20d         | SPY    | 14:30   |        3 | 100%  |   33.73 |    29.07 |    27.4  |  101.2  |    27.4  |    73.8  |
| L1 long straddle      | SPXW   | 10:00   |        4 | 50%   |   36.25 | -2379.01 | -3676    |  144.98 |  -232    |   376.98 |
| L1 long straddle      | SPXW   | 11:30   |        4 | 50%   | -209.5  | -1534.75 | -2066    | -837.98 |   193    | -1030.98 |
| L1 long straddle      | SPXW   | 13:00   |        4 | 50%   |   98    |  -656.49 | -1159.98 |  392.02 |  1948    | -1555.98 |
| L1 long straddle      | SPXW   | 14:30   |        3 | 33%   |   77.33 |  -566    |  -806    |  232    |  1124    |  -892    |
| L1 long straddle      | SPY    | 10:00   |        4 | 50%   |    7.4  |  -221.6  |  -346.6  |   29.6  |    52.8  |   -23.2  |
| L1 long straddle      | SPY    | 11:30   |        4 | 50%   |  -31.85 |  -155.35 |  -178.6  | -127.4  |     9.8  |  -137.2  |
| L1 long straddle      | SPY    | 13:00   |        4 | 50%   |  -20.6  |  -111.6  |  -163.6  |  -82.4  |   141.8  |  -224.2  |
| L1 long straddle      | SPY    | 14:30   |        3 | 33%   |   -6.27 |   -60.6  |   -82.6  |  -18.8  |    80.4  |   -99.2  |
| T1 trend spread 15d   | SPXW   | 10:00   |        4 | 100%  |  190.75 |   187    |   187    |  763    |   389    |   374    |
| T1 trend spread 15d   | SPXW   | 11:30   |        4 | 100%  |  147    |   123.25 |   107    |  588    |   319    |   269    |
| T1 trend spread 15d   | SPXW   | 13:00   |        4 | 75%   | -145    |  -422.01 |  -941.02 | -580.02 |  -829.02 |   249    |
| T1 trend spread 15d   | SPXW   | 14:30   |        3 | 100%  |  102    |    73.67 |    57    |  306    |    57    |   249    |
| T1 trend spread 15d   | SPY    | 10:00   |        4 | 100%  |   21.45 |    17.7  |    17.7  |   85.8  |    50.4  |    35.4  |
| T1 trend spread 15d   | SPY    | 11:30   |        4 | 100%  |   14.2  |    11.45 |     9.7  |   56.8  |    33.4  |    23.4  |
| T1 trend spread 15d   | SPY    | 13:00   |        4 | 75%   |   -9.3  |   -31.3  |   -73.3  |  -37.2  |   -61.6  |    24.4  |
| T1 trend spread 15d   | SPY    | 14:30   |        3 | 100%  |    9.03 |     5.7  |     3.7  |   27.1  |     3.7  |    23.4  |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             258 |               8447 |                   576 |
| 2026-11-10 |            -1130 |             345 |                     462 |            -199 |              -5231 |                  -497 |
| 2026-11-11 |              858 |             648 |                    -245 |             807 |                257 |                   588 |
| 2026-11-12 |             1649 |             648 |                     -37 |            1691 |              -3740 |                   543 |
