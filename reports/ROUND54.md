# Round 54: NY-session grid + segment scanner on 7 markets

Rules: [PROTOCOL_ROUND54.md](../PROTOCOL_ROUND54.md). Markets with data: EURUSD, GBPUSD, GOLD, NQ, OIL, SP, USDJPY.

## Detector 1: grid

Configurations: **12096**. Screen (ho t ≥ 3, dev t ≥ 2): **0**. Of those, beating the expected best-of-12096 t (4.34): **0**.

Share of configurations with holdout mean R > 0, by market: EURUSD 8%, GBPUSD 9%, GOLD 10%, NQ 37%, OIL 19%, SP 33%, USDJPY 14%

Top 15 by the weaker period's t:

| market   | entry          | stop      | target      | exit   | filter   |   dev_n |   dev_meanR |   dev_t |   ho_n |   ho_meanR |   ho_t |
|:---------|:---------------|:----------|:------------|:-------|:---------|--------:|------------:|--------:|-------:|-----------:|-------:|
| USDJPY   | PrevDayBreak   | 0.25%     | time        | 15:55  | low_vol  |     365 |       0.134 |   2.474 |    193 |      0.173 |  2.535 |
| USDJPY   | PrevDayBreak   | 0.5%      | 3R          | 15:55  | low_vol  |     365 |       0.079 |   2.686 |    193 |      0.088 |  2.446 |
| USDJPY   | PrevDayBreak   | 0.5%      | time        | 15:55  | low_vol  |     365 |       0.082 |   2.705 |    193 |      0.088 |  2.446 |
| USDJPY   | PrevDayBreak   | 0.5%      | 2R          | 15:55  | low_vol  |     365 |       0.072 |   2.588 |    193 |      0.083 |  2.428 |
| USDJPY   | PrevDayBreak   | 0.25%     | 3R          | 15:55  | low_vol  |     365 |       0.111 |   2.261 |    193 |      0.175 |  2.714 |
| USDJPY   | PrevDayBreak   | 0.5%      | 1R          | 15:55  | low_vol  |     365 |       0.055 |   2.204 |    193 |      0.078 |  2.438 |
| USDJPY   | PrevDayBreak   | structure | 2R          | 15:55  | low_vol  |     365 |       0.094 |   2.385 |    193 |      0.107 |  2.078 |
| USDJPY   | PrevDayBreak   | 0.25%     | 2R          | 15:55  | low_vol  |     365 |       0.096 |   2.071 |    193 |      0.153 |  2.561 |
| USDJPY   | PrevDayBreak   | structure | time        | 15:55  | low_vol  |     365 |       0.1   |   2.396 |    193 |      0.108 |  1.881 |
| USDJPY   | PrevDayBreak   | structure | 3R          | 15:55  | low_vol  |     365 |       0.102 |   2.448 |    193 |      0.094 |  1.816 |
| SP       | GapFill0.5     | 0.5%      | prior close | 15:55  | low_vol  |     194 |       0.141 |   1.742 |    159 |      0.161 |  1.689 |
| USDJPY   | PrevDayBreak   | structure | 1R          | 15:55  | low_vol  |     365 |       0.055 |   1.673 |    193 |      0.087 |  1.858 |
| NQ       | ORB60          | structure | time        | 15:55  | with_gap |    1034 |       0.084 |   1.618 |    653 |      0.154 |  2.37  |
| SP       | GapFill0.5     | 0.25%     | prior close | 15:55  | low_vol  |     194 |       0.289 |   2.144 |    159 |      0.238 |  1.586 |
| SP       | OvernightBreak | 0.25%     | time        | 15:55  | low_vol  |     320 |       0.152 |   1.502 |    545 |      0.14  |  1.915 |

## Detector 2: segment scanner

Tests: 1869; Bonferroni |t| ≥ 4.20, same sign both periods, |mean| > cost + 1 bp in both.

Significant: **0**; also beating costs: **0**.

Nothing significant. Top 15 by |t|:

| market   | signal               | target      |   n_dev |   bp_dev |   t_dev |   n_ho |   bp_ho |   t_ho |   t_all |
|:---------|:---------------------|:------------|--------:|---------:|--------:|-------:|--------:|-------:|--------:|
| OIL      | weekday4             | 12:00→close |     332 |    19.46 |    3.06 |    140 |   10.64 |   1.14 |    3.18 |
| USDJPY   | overnight/gap        | 09:45→12:00 |    2088 |     1.19 |    2.39 |   1316 |    1.31 |   2.1  |    3.18 |
| EURUSD   | open→10:00           | 10:00→14:00 |    2265 |    -0.97 |   -1.81 |   1365 |   -1.87 |  -2.76 |   -3.12 |
| EURUSD   | weekday3             | 10:00→10:30 |     458 |    -1.49 |   -2.5  |    275 |   -1.41 |  -1.64 |   -2.98 |
| EURUSD   | narrowday×open→10:00 | 10:00→14:00 |    1138 |    -1.2  |   -1.7  |    688 |   -2.32 |  -2.49 |   -2.87 |
| USDJPY   | overnight/gap        | open→12:00  |    2088 |     1.11 |    1.97 |   1316 |    1.63 |   2.13 |    2.87 |
| EURUSD   | narrowday×open→10:00 | 12:00→14:00 |    1138 |    -0.73 |   -1.83 |    688 |   -1.18 |  -2.28 |   -2.85 |
| NQ       | weekday1             | 14:00→15:00 |     438 |     2.29 |    1.67 |    277 |    4.89 |   2.39 |    2.79 |
| EURUSD   | open→10:00           | 10:00→15:00 |    2265 |    -1.05 |   -1.8  |   1365 |   -1.58 |  -2.2  |   -2.77 |
| EURUSD   | narrowday×open→10:00 | 10:30→14:00 |    1138 |    -1.13 |   -1.73 |    688 |   -1.88 |  -2.28 |   -2.77 |
| NQ       | open→15:00           | 15:00→close |    2137 |     0.8  |    1.04 |   1327 |    3.2  |   3.14 |    2.76 |
| NQ       | weekday0             | open→close  |     392 |     7.35 |    1.69 |    247 |   14.06 |   2.25 |    2.72 |
| EURUSD   | open→10:00           | 10:30→14:00 |    2265 |    -0.83 |   -1.71 |   1365 |   -1.36 |  -2.23 |   -2.72 |
| NQ       | overnight/gap        | open→09:45  |    2136 |    -0.93 |   -1.9  |   1327 |   -1.89 |  -1.95 |   -2.7  |
| EURUSD   | narrowday×open→10:00 | 10:00→15:00 |    1138 |    -1.1  |   -1.42 |    688 |   -2.55 |  -2.53 |   -2.67 |
| OIL      | weekday4             | 14:00→close |     332 |    12.17 |    2.55 |    140 |    4.78 |   0.97 |    2.67 |
| NQ       | weekday0             | open→09:45  |     392 |     1.11 |    1.02 |    247 |    4.53 |   3    |    2.66 |
| USDJPY   | weekday1             | 14:00→close |     424 |     1.64 |    2.41 |    271 |    0.77 |   1.24 |    2.65 |
| EURUSD   | weekday0             | open→09:45  |     431 |     1.02 |    3.12 |    258 |    0.11 |   0.26 |    2.62 |
| NQ       | weekday0             | open→15:00  |     392 |     5.78 |    1.52 |    247 |   13.26 |   2.28 |    2.61 |
| EURUSD   | open→10:00           | 10:00→close |    2265 |    -1.28 |   -2.06 |   1365 |   -1.21 |  -1.59 |   -2.6  |
| NQ       | weekday0             | 10:30→close |     392 |     8.56 |    2.01 |    247 |    9.18 |   1.58 |    2.55 |
| EURUSD   | narrowday×open→10:00 | 10:30→15:00 |    1138 |    -1.02 |   -1.42 |    688 |   -2.11 |  -2.33 |   -2.55 |
| GBPUSD   | weekday0             | open→10:00  |     437 |     1.3  |    2.63 |    260 |    0.45 |   0.76 |    2.55 |
| EURUSD   | open→10:00           | 10:00→12:00 |    2265 |    -0.42 |   -0.94 |   1365 |   -1.6  |  -2.92 |   -2.53 |

