# Round 62b: direction study on Yahoo 1-minute data (SPY + market-wide + calendar variables)

Rules: [PROTOCOL_ROUND62.md](../PROTOCOL_ROUND62.md) amendment 5. 100 SPY shares per trade (~$74k), 1¢/share each way. Leave-one-day-out.
Days: **21** (2026-10-23 → 2026-11-20); minutes analysed: 7,266; variables: 52.

- 10-min horizon: best model policy $2,907 vs best no-model baseline $7,014; model ≥60% long/short $-2,389 vs time-shift null 95th pct $5,024.
- 30-min horizon: best model policy $6,912 vs best no-model baseline $9,800; model ≥60% long/short $323 vs time-shift null 95th pct $7,996.
- 60-min horizon: best model policy $5,505 vs best no-model baseline $11,789; model ≥60% long/short $32 vs time-shift null 95th pct $6,086.

| horizon   | policy                | selectivity   | walk_away   |   trades |   total |   win | green   |     t |
|:----------|:----------------------|:--------------|:------------|---------:|--------:|------:|:--------|------:|
| 60m       | BASELINE always short | every slot    | False       |      126 |   11789 |  0.56 | 13/21   |  2.24 |
| 30m       | BASELINE always short | every slot    | False       |      252 |    9800 |  0.55 | 13/21   |  2.13 |
| 10m       | BASELINE always short | every slot    | False       |      756 |    7014 |  0.53 | 10/21   |  1.73 |
| 30m       | short_only            | every slot    | False       |      197 |    6912 |  0.54 | 14/21   |  1.86 |
| 60m       | short_only            | every slot    | False       |       97 |    5505 |  0.58 | 13/21   |  2.04 |
| 60m       | short_only            | ≥60%          | False       |       89 |    5287 |  0.55 | 13/20   |  1.7  |
| 30m       | short_only            | ≥60%          | False       |      171 |    5259 |  0.52 | 14/21   |  1.81 |
| 60m       | short_only            | ≥70%          | False       |       80 |    4871 |  0.56 | 13/19   |  1.66 |
| 60m       | short_only            | every slot    | True        |       34 |    3341 |  0.59 | 16/21   |  1.88 |
| 30m       | short_only            | ≥70%          | False       |      131 |    3288 |  0.54 | 15/20   |  1.79 |
| 10m       | short_only            | ≥60%          | False       |      362 |    2907 |  0.51 | 16/21   |  1.53 |
| 10m       | short_only            | every slot    | False       |      515 |    2819 |  0.51 | 10/21   |  1.07 |
| 60m       | short_only            | ≥60%          | True        |       35 |    2670 |  0.54 | 14/20   |  1.59 |
| 60m       | short_only            | ≥70%          | True        |       33 |    2496 |  0.52 | 14/19   |  1.47 |
| 30m       | short_only            | ≥70%          | True        |       37 |    2411 |  0.54 | 16/20   |  1.86 |
| 30m       | short_only            | ≥60%          | True        |       41 |    1754 |  0.49 | 15/21   |  1.56 |
| 60m       | long_short            | ≥60%          | True        |       37 |    1294 |  0.54 | 15/21   |  0.51 |
| 30m       | short_only            | every slot    | True        |       48 |    1138 |  0.44 | 13/21   |  0.97 |
| 30m       | long_short            | ≥70%          | True        |       37 |    1066 |  0.57 | 16/21   |  0.53 |
| 10m       | short_only            | ≥70%          | False       |      224 |     856 |  0.52 | 15/21   |  0.79 |
| 60m       | long_short            | every slot    | True        |       41 |     789 |  0.46 | 15/21   |  0.28 |
| 10m       | short_only            | ≥60%          | True        |       39 |     688 |  0.54 | 17/21   |  0.93 |
| 30m       | long_short            | ≥60%          | True        |       40 |     424 |  0.52 | 15/21   |  0.23 |
| 10m       | short_only            | ≥70%          | True        |       44 |     421 |  0.48 | 13/21   |  0.74 |
| 30m       | long_short            | ≥70%          | False       |      200 |     326 |  0.55 | 16/21   |  0.11 |
| 30m       | long_short            | ≥60%          | False       |      242 |     323 |  0.51 | 12/21   |  0.12 |
| 60m       | long_short            | ≥70%          | False       |      112 |     243 |  0.47 | 12/21   |  0.06 |
| 60m       | long_short            | ≥60%          | False       |      123 |      32 |  0.51 | 10/21   |  0.01 |
| 60m       | long_short            | ≥70%          | True        |       41 |    -149 |  0.44 | 15/21   | -0.05 |
| 60m       | long_short            | every slot    | False       |      126 |    -393 |  0.49 | 11/21   | -0.11 |
| 10m       | long_short            | ≥60%          | True        |       42 |    -492 |  0.5  | 15/21   | -0.46 |
| 10m       | short_only            | every slot    | True        |       49 |    -581 |  0.43 | 8/21    | -0.72 |
| 30m       | long_short            | every slot    | False       |      252 |    -625 |  0.52 | 12/21   | -0.2  |
| 10m       | long_only             | every slot    | True        |       41 |    -771 |  0.51 | 14/21   | -0.75 |
| 30m       | long_only             | ≥70%          | True        |       26 |    -954 |  0.58 | 11/16   | -0.54 |
| 30m       | long_short            | every slot    | True        |       43 |    -984 |  0.49 | 14/21   | -0.51 |
| 10m       | long_short            | ≥70%          | True        |       48 |    -995 |  0.44 | 12/21   | -0.81 |
| 10m       | long_short            | every slot    | True        |       59 |   -1508 |  0.36 | 11/21   | -1.39 |
| 30m       | long_only             | ≥60%          | True        |       31 |   -1534 |  0.52 | 10/18   | -0.85 |
| 10m       | long_only             | ≥70%          | True        |       32 |   -2156 |  0.34 | 6/14    | -1.79 |
| 10m       | long_only             | ≥60%          | True        |       43 |   -2336 |  0.42 | 8/19    | -1.95 |
| 10m       | long_short            | ≥60%          | False       |      603 |   -2389 |  0.49 | 12/21   | -1.07 |
| 30m       | long_only             | every slot    | True        |       39 |   -2497 |  0.49 | 13/20   | -1.11 |
| 10m       | long_short            | ≥70%          | False       |      357 |   -2761 |  0.46 | 11/21   | -1.27 |
| 30m       | long_only             | ≥70%          | False       |       86 |   -3281 |  0.5  | 9/16    | -1.18 |
| 60m       | long_only             | ≥70%          | True        |       26 |   -3692 |  0.31 | 7/14    | -1.61 |
| 10m       | long_only             | ≥70%          | False       |      134 |   -3823 |  0.36 | 4/14    | -2.06 |
| 10m       | long_only             | ≥60%          | False       |      265 |   -4649 |  0.46 | 8/19    | -1.91 |
| 30m       | long_only             | ≥60%          | False       |      117 |   -4722 |  0.44 | 7/18    | -1.71 |
| 60m       | long_only             | ≥70%          | False       |       43 |   -4858 |  0.3  | 6/14    | -1.85 |
| 60m       | long_only             | ≥60%          | True        |       33 |   -4962 |  0.36 | 8/16    | -1.93 |
| 60m       | long_only             | every slot    | True        |       41 |   -5276 |  0.34 | 9/18    | -2    |
| 10m       | long_short            | every slot    | False       |      735 |   -5569 |  0.48 | 7/21    | -2.37 |
| 30m       | long_only             | every slot    | False       |      156 |   -6494 |  0.44 | 7/20    | -2.03 |
| 60m       | long_only             | ≥60%          | False       |       57 |   -6745 |  0.32 | 5/16    | -2.39 |
| 60m       | long_only             | every slot    | False       |       69 |   -7353 |  0.35 | 6/18    | -2.32 |
| 10m       | long_only             | every slot    | False       |      412 |   -7826 |  0.43 | 10/21   | -2.2  |
| 10m       | BASELINE always long  | every slot    | False       |      756 |  -10038 |  0.45 | 7/21    | -2.47 |
| 30m       | BASELINE always long  | every slot    | False       |      252 |  -10808 |  0.44 | 7/21    | -2.35 |
| 60m       | BASELINE always long  | every slot    | False       |      126 |  -12293 |  0.44 | 8/21    | -2.34 |
