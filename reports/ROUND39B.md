# Round 39b: 0DTE paper strategies on collected Cboe quotes

Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; first score at 20 trading days, again at 40. P&L per 1 lot.

- 2026-11-09 SPXW: 409 snapshots, settle 7549.83 (last snapshot), 21 trades
- 2026-11-09 SPY: 382 snapshots, settle 752.77 (last snapshot), 21 trades

Trading days scored: **1** (verdict at 20).

| strategy              | root   | entry   |   trades | win   |    mean |   low90 |   worst |   total |   h1 |   h2 |
|:----------------------|:-------|:--------|---------:|:------|--------:|--------:|--------:|--------:|-----:|-----:|
| B1 OR breakout        | SPXW   | -       |        1 | 100%  | 2327    |     nan | 2327    | 2327    |  nan |  nan |
| B1 OR breakout        | SPY    | -       |        1 | 100%  |  274.7  |     nan |  274.7  |  274.7  |  nan |  nan |
| I1 condor 10d         | SPXW   | 10:00   |        1 | 100%  |  254    |     nan |  254    |  254    |  nan |  nan |
| I1 condor 10d         | SPXW   | 11:30   |        1 | 100%  |  204    |     nan |  204    |  204    |  nan |  nan |
| I1 condor 10d         | SPXW   | 13:00   |        1 | 100%  |  139    |     nan |  139    |  139    |  nan |  nan |
| I1 condor 10d         | SPXW   | 14:30   |        1 | 100%  |   89    |     nan |   89    |   89    |  nan |  nan |
| I1 condor 10d         | SPY    | 10:00   |        1 | 100%  |   29.4  |     nan |   29.4  |   29.4  |  nan |  nan |
| I1 condor 10d         | SPY    | 11:30   |        1 | 100%  |   15.4  |     nan |   15.4  |   15.4  |  nan |  nan |
| I1 condor 10d         | SPY    | 13:00   |        1 | 100%  |   10.4  |     nan |   10.4  |   10.4  |  nan |  nan |
| I1 condor 10d         | SPY    | 14:30   |        1 | 100%  |    8.4  |     nan |    8.4  |    8.4  |  nan |  nan |
| I2 condor 10d stop 2x | SPXW   | 10:00   |        1 | 0%    | -342    |     nan | -342    | -342    |  nan |  nan |
| I2 condor 10d stop 2x | SPXW   | 11:30   |        1 | 0%    | -392    |     nan | -392    | -392    |  nan |  nan |
| I2 condor 10d stop 2x | SPXW   | 13:00   |        1 | 0%    | -192    |     nan | -192    | -192    |  nan |  nan |
| I2 condor 10d stop 2x | SPXW   | 14:30   |        1 | 0%    | -147    |     nan | -147    | -147    |  nan |  nan |
| I2 condor 10d stop 2x | SPY    | 10:00   |        1 | 0%    |  -51.2  |     nan |  -51.2  |  -51.2  |  nan |  nan |
| I2 condor 10d stop 2x | SPY    | 11:30   |        1 | 0%    |  -28.2  |     nan |  -28.2  |  -28.2  |  nan |  nan |
| I2 condor 10d stop 2x | SPY    | 13:00   |        1 | 0%    |  -18.2  |     nan |  -18.2  |  -18.2  |  nan |  nan |
| I2 condor 10d stop 2x | SPY    | 14:30   |        1 | 0%    |  -38.2  |     nan |  -38.2  |  -38.2  |  nan |  nan |
| I3 condor 20d         | SPXW   | 10:00   |        1 | 0%    | -839.01 |     nan | -839.01 | -839.01 |  nan |  nan |
| I3 condor 20d         | SPXW   | 11:30   |        1 | 100%  |  484    |     nan |  484    |  484    |  nan |  nan |
| I3 condor 20d         | SPXW   | 13:00   |        1 | 100%  |  319    |     nan |  319    |  319    |  nan |  nan |
| I3 condor 20d         | SPXW   | 14:30   |        1 | 100%  |  189    |     nan |  189    |  189    |  nan |  nan |
| I3 condor 20d         | SPY    | 10:00   |        1 | 0%    |  -15.6  |     nan |  -15.6  |  -15.6  |  nan |  nan |
| I3 condor 20d         | SPY    | 11:30   |        1 | 100%  |   50.4  |     nan |   50.4  |   50.4  |  nan |  nan |
| I3 condor 20d         | SPY    | 13:00   |        1 | 100%  |   45.4  |     nan |   45.4  |   45.4  |  nan |  nan |
| I3 condor 20d         | SPY    | 14:30   |        1 | 100%  |   27.4  |     nan |   27.4  |   27.4  |  nan |  nan |
| L1 long straddle      | SPXW   | 10:00   |        1 | 100%  | 3444    |     nan | 3444    | 3444    |  nan |  nan |
| L1 long straddle      | SPXW   | 11:30   |        1 | 100%  | 2259    |     nan | 2259    | 2259    |  nan |  nan |
| L1 long straddle      | SPXW   | 13:00   |        1 | 100%  |  854    |     nan |  854    |  854    |  nan |  nan |
| L1 long straddle      | SPXW   | 14:30   |        1 | 100%  | 1124    |     nan | 1124    | 1124    |  nan |  nan |
| L1 long straddle      | SPY    | 10:00   |        1 | 100%  |  399.4  |     nan |  399.4  |  399.4  |  nan |  nan |
| L1 long straddle      | SPY    | 11:30   |        1 | 100%  |  188.4  |     nan |  188.4  |  188.4  |  nan |  nan |
| L1 long straddle      | SPY    | 13:00   |        1 | 100%  |   97.4  |     nan |   97.4  |   97.4  |  nan |  nan |
| L1 long straddle      | SPY    | 14:30   |        1 | 100%  |   80.4  |     nan |   80.4  |   80.4  |  nan |  nan |
| T1 trend spread 15d   | SPXW   | 10:00   |        1 | 100%  |  202    |     nan |  202    |  202    |  nan |  nan |
| T1 trend spread 15d   | SPXW   | 11:30   |        1 | 100%  |  147    |     nan |  147    |  147    |  nan |  nan |
| T1 trend spread 15d   | SPXW   | 13:00   |        1 | 100%  |  112    |     nan |  112    |  112    |  nan |  nan |
| T1 trend spread 15d   | SPXW   | 14:30   |        1 | 100%  |   57    |     nan |   57    |   57    |  nan |  nan |
| T1 trend spread 15d   | SPY    | 10:00   |        1 | 100%  |   25.7  |     nan |   25.7  |   25.7  |  nan |  nan |
| T1 trend spread 15d   | SPY    | 11:30   |        1 | 100%  |   16.7  |     nan |   16.7  |   16.7  |  nan |  nan |
| T1 trend spread 15d   | SPY    | 13:00   |        1 | 100%  |   11.7  |     nan |   11.7  |   11.7  |  nan |  nan |
| T1 trend spread 15d   | SPY    | 14:30   |        1 | 100%  |    3.7  |     nan |    3.7  |    3.7  |  nan |  nan |

Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.

## Daily P&L by strategy (all entries and both roots)

| day        |   B1 OR breakout |   I1 condor 10d |   I2 condor 10d stop 2x |   I3 condor 20d |   L1 long straddle |   T1 trend spread 15d |
|:-----------|-----------------:|----------------:|------------------------:|----------------:|-------------------:|----------------------:|
| 2026-11-09 |             2602 |             750 |                   -1209 |             261 |               8447 |                   576 |
