# Round 53: exhaustive New York-session grid (S&P and Nasdaq micros)

Rules: [PROTOCOL_ROUND53.md](../PROTOCOL_ROUND53.md). Configurations run: **3456** (1728 per market). Holdout = 2021 → now. Runtime 36 s.

Screen (holdout t ≥ 3 and dev t ≥ 2, both positive): **0** candidates. Full pass (also deflated Sharpe ≥ 0.95, positive on the other market, prop pass ≥ 50%, EV > 0): **0**.

## Top 40 by holdout t (all configurations)

| market   | entry          | stop      | target   | exit   | filter       |   dev_n |   dev_meanR |   dev_t |   ho_n |   ho_meanR |   ho_t |   ho_win |   ho_usd_month |
|:---------|:---------------|:----------|:---------|:-------|:-------------|--------:|------------:|--------:|-------:|-----------:|-------:|---------:|---------------:|
| NQ       | PowerHour0.3   | 0.5%      | 3R       | 15:59  | with_trend20 |     645 |      -0.038 |  -1.548 |    483 |      0.095 |  2.918 |    0.522 |        103.603 |
| NQ       | PowerHour0.3   | 0.5%      | time     | 15:59  | with_trend20 |     645 |      -0.039 |  -1.581 |    483 |      0.093 |  2.868 |    0.522 |        100.99  |
| NQ       | PowerHour0.3   | 0.5%      | 2R       | 15:59  | with_trend20 |     645 |      -0.037 |  -1.543 |    483 |      0.091 |  2.865 |    0.522 |         98.206 |
| NQ       | ORB60          | structure | time     | 15:55  | none         |    2099 |       0.009 |   0.252 |   1295 |      0.119 |  2.797 |    0.436 |        468.797 |
| NQ       | ORB60          | structure | time     | 15:55  | with_gap     |    1034 |       0.045 |   0.873 |    653 |      0.172 |  2.654 |    0.447 |        303.259 |
| NQ       | ORB60          | structure | time     | 15:55  | with_trend20 |    1050 |      -0.012 |  -0.243 |    654 |      0.152 |  2.589 |    0.454 |        286.144 |
| NQ       | FirstHour0.2   | 0.5%      | time     | 15:55  | with_trend20 |     345 |      -0.051 |  -0.726 |    332 |      0.234 |  2.495 |    0.434 |        195.469 |
| NQ       | PowerHour0.3   | 0.5%      | 3R       | 15:59  | none         |    1298 |      -0.024 |  -1.361 |    957 |      0.057 |  2.45  |    0.504 |         99.426 |
| NQ       | PowerHour0.3   | 0.25%     | time     | 15:59  | with_trend20 |     645 |      -0.069 |  -1.657 |    483 |      0.14  |  2.449 |    0.46  |        200.078 |
| NQ       | PowerHour0.3   | 0.5%      | time     | 15:59  | none         |    1298 |      -0.022 |  -1.228 |    957 |      0.057 |  2.44  |    0.504 |         99.806 |
| NQ       | ORB60          | structure | time     | 15:55  | low_vol      |    1015 |       0.031 |   0.58  |    636 |      0.148 |  2.401 |    0.426 |        280.516 |
| NQ       | ORB60          | 0.5%      | 3R       | 15:55  | low_vol      |    1015 |       0.008 |   0.242 |    636 |      0.121 |  2.39  |    0.456 |        194.306 |
| NQ       | ORfade15       | structure | time     | 15:55  | low_vol      |     971 |      -0.395 |  -2.36  |    607 |      0.708 |  2.385 |    0.171 |        955.997 |
| NQ       | PowerHour0.3   | 0.25%     | 3R       | 15:59  | with_trend20 |     645 |      -0.055 |  -1.392 |    483 |      0.124 |  2.352 |    0.462 |        175.29  |
| NQ       | ORB60          | 0.5%      | time     | 15:55  | low_vol      |    1015 |       0.002 |   0.05  |    636 |      0.123 |  2.316 |    0.453 |        211.944 |
| NQ       | PrevDayBreak   | structure | 2R       | 15:55  | none         |     978 |      -0.022 |  -1.112 |    640 |      0.056 |  2.31  |    0.552 |        193.966 |
| NQ       | ORfade15       | 0.25%     | 3R       | 15:55  | low_vol      |     973 |      -0.047 |  -0.979 |    607 |      0.158 |  2.305 |    0.349 |        220.191 |
| NQ       | PowerHour0.3   | 0.25%     | time     | 15:59  | none         |    1298 |      -0.044 |  -1.397 |    957 |      0.094 |  2.289 |    0.45  |        277.778 |
| NQ       | ORB60          | structure | time     | 15:55  | skip_mon_fri |    1311 |      -0.008 |  -0.172 |    795 |      0.128 |  2.26  |    0.424 |        266.141 |
| NQ       | ORfade15       | 0.25%     | 3R       | 11:30  | low_vol      |     938 |      -0.042 |  -1.054 |    576 |      0.136 |  2.255 |    0.415 |        163.713 |
| NQ       | ORfade15       | 0.5%      | 3R       | 15:55  | none         |    2019 |      -0.009 |  -0.328 |   1237 |      0.087 |  2.252 |    0.414 |        277.541 |
| NQ       | ORfade15       | 0.25%     | time     | 11:30  | low_vol      |     938 |      -0.023 |  -0.551 |    576 |      0.15  |  2.24  |    0.406 |        197.432 |
| NQ       | PowerHour0.3   | 0.5%      | 2R       | 15:59  | none         |    1298 |      -0.027 |  -1.574 |    957 |      0.049 |  2.209 |    0.504 |         80.772 |
| NQ       | ORfade15       | structure | time     | 11:30  | low_vol      |     936 |      -0.524 |  -3.853 |    576 |      0.447 |  2.207 |    0.233 |        586.537 |
| NQ       | ORB60          | structure | 3R       | 15:55  | low_vol      |    1015 |      -0.006 |  -0.132 |    636 |      0.117 |  2.166 |    0.431 |        214.8   |
| NQ       | ORB30          | structure | time     | 15:55  | none         |    2126 |      -0.062 |  -1.297 |   1322 |      0.12  |  2.135 |    0.359 |        494.58  |
| NQ       | ORB60          | structure | 3R       | 15:55  | with_trend20 |    1050 |      -0.059 |  -1.458 |    654 |      0.109 |  2.133 |    0.459 |        210.139 |
| NQ       | ORfade15       | 0.5%      | 3R       | 15:55  | low_vol      |     973 |       0.02  |   0.554 |    607 |      0.115 |  2.125 |    0.43  |        175.637 |
| NQ       | ORfade15       | 0.5%      | time     | 15:55  | low_vol      |     973 |       0.019 |   0.517 |    607 |      0.127 |  2.117 |    0.423 |        198.653 |
| NQ       | PrevDayBreak   | structure | 3R       | 15:55  | none         |     978 |      -0.021 |  -1.035 |    640 |      0.05  |  2.105 |    0.55  |        182.992 |
| NQ       | PrevDayBreak   | structure | time     | 15:55  | none         |     978 |      -0.022 |  -1.115 |    640 |      0.05  |  2.105 |    0.55  |        182.992 |
| NQ       | ORfade15       | structure | time     | 15:55  | none         |    2010 |      -0.429 |  -4.065 |   1237 |      0.459 |  2.096 |    0.16  |       1021.35  |
| NQ       | OvernightBreak | 0.5%      | time     | 15:55  | low_vol      |     874 |      -0.067 |  -1.83  |    522 |      0.124 |  2.08  |    0.45  |        183.811 |
| NQ       | OvernightBreak | 0.5%      | 3R       | 15:55  | low_vol      |     874 |      -0.067 |  -1.868 |    522 |      0.115 |  2.066 |    0.454 |        157.325 |
| NQ       | PrevDayBreak   | structure | 2R       | 15:55  | with_trend20 |     525 |      -0.029 |  -1.119 |    364 |      0.064 |  2.057 |    0.569 |        150.158 |
| NQ       | PrevDayBreak   | structure | 3R       | 15:55  | with_trend20 |     525 |      -0.028 |  -1.107 |    364 |      0.064 |  2.055 |    0.569 |        149.799 |
| NQ       | PrevDayBreak   | structure | time     | 15:55  | with_trend20 |     525 |      -0.028 |  -1.107 |    364 |      0.064 |  2.055 |    0.569 |        149.799 |
| NQ       | ORB60          | structure | 3R       | 15:55  | none         |    2099 |      -0.03  |  -1.017 |   1295 |      0.073 |  2.044 |    0.439 |        288.362 |
| NQ       | ORfade15       | 0.5%      | time     | 15:55  | none         |    2019 |      -0.008 |  -0.28  |   1237 |      0.088 |  2.034 |    0.403 |        267.471 |
| NQ       | ORfade15       | 0.5%      | 3R       | 11:30  | low_vol      |     938 |      -0.021 |  -0.882 |    576 |      0.08  |  2.022 |    0.493 |        128.867 |

## Share of configurations with holdout mean R > 0, by entry family

| entry          | NQ         | SP         |
|:---------------|:-----------|:-----------|
| FirstHour0.2   | 28% of 96  | 26% of 96  |
| FirstHour0.4   | 30% of 96  | 29% of 96  |
| GapFill0.2     | 42% of 24  | 50% of 24  |
| GapFill0.5     | 38% of 24  | 38% of 24  |
| GapGo0.2       | 84% of 96  | 40% of 96  |
| GapGo0.5       | 82% of 96  | 85% of 96  |
| ORB15          | 26% of 144 | 17% of 144 |
| ORB30          | 19% of 144 | 11% of 144 |
| ORB5           | 20% of 144 | 8% of 144  |
| ORB60          | 72% of 144 | 33% of 144 |
| ORfade15       | 73% of 144 | 26% of 144 |
| ORfade30       | 71% of 144 | 24% of 144 |
| OvernightBreak | 49% of 144 | 24% of 144 |
| PowerHour0.3   | 100% of 48 | 96% of 48  |
| PrevDayBreak   | 60% of 144 | 67% of 144 |
| StretchFade0.5 | 12% of 96  | 40% of 96  |
