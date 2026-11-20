# Round 62b: direction study on Yahoo 1-minute data (SPY + market-wide + calendar variables)

Rules: [PROTOCOL_ROUND62.md](../PROTOCOL_ROUND62.md) amendment 5. 100 SPY shares per trade (~$74k), 1¢/share each way. Leave-one-day-out.
Days: **20** (2026-10-23 → 2026-11-19); minutes analysed: 6,920; variables: 52.

- 10-min horizon: best model policy $3,401 vs best no-model baseline $5,207; model ≥60% long/short $-1,740 vs time-shift null 95th pct $2,297.
- 30-min horizon: best model policy $4,911 vs best no-model baseline $7,218; model ≥60% long/short $-199 vs time-shift null 95th pct $3,530.
- 60-min horizon: best model policy $3,423 vs best no-model baseline $8,891; model ≥60% long/short $-1,923 vs time-shift null 95th pct $3,174.

| horizon   | policy                | selectivity   | walk_away   |   trades |   total |   win | green   |     t |
|:----------|:----------------------|:--------------|:------------|---------:|--------:|------:|:--------|------:|
| 60m       | BASELINE always short | every slot    | False       |      120 |    8891 |  0.54 | 12/20   |  1.91 |
| 30m       | BASELINE always short | every slot    | False       |      240 |    7218 |  0.54 | 12/20   |  1.79 |
| 10m       | BASELINE always short | every slot    | False       |      720 |    5207 |  0.52 | 9/20    |  1.39 |
| 30m       | short_only            | every slot    | False       |      185 |    4911 |  0.56 | 14/20   |  2.04 |
| 60m       | short_only            | every slot    | False       |       85 |    3423 |  0.59 | 12/19   |  1.76 |
| 10m       | short_only            | ≥60%          | False       |      343 |    3401 |  0.52 | 11/20   |  1.42 |
| 60m       | short_only            | ≥70%          | False       |       70 |    3188 |  0.57 | 14/19   |  2.13 |
| 60m       | short_only            | ≥60%          | False       |       75 |    3175 |  0.57 | 15/19   |  2.1  |
| 30m       | short_only            | ≥60%          | False       |      157 |    3104 |  0.54 | 14/20   |  1.53 |
| 30m       | short_only            | ≥70%          | False       |      126 |    3031 |  0.54 | 15/19   |  1.96 |
| 10m       | short_only            | every slot    | False       |      481 |    2998 |  0.49 | 10/20   |  1.12 |
| 60m       | short_only            | every slot    | True        |       33 |    2826 |  0.55 | 13/19   |  1.65 |
| 30m       | short_only            | every slot    | True        |       40 |    2340 |  0.5  | 16/20   |  1.76 |
| 30m       | short_only            | ≥70%          | True        |       34 |    2315 |  0.56 | 16/19   |  2.08 |
| 60m       | short_only            | ≥60%          | True        |       31 |    2298 |  0.58 | 14/19   |  1.58 |
| 60m       | short_only            | ≥70%          | True        |       34 |    2252 |  0.53 | 14/19   |  1.51 |
| 30m       | long_short            | every slot    | True        |       36 |    1879 |  0.56 | 15/20   |  1.63 |
| 30m       | short_only            | ≥60%          | True        |       39 |    1566 |  0.51 | 13/20   |  1.2  |
| 30m       | long_short            | ≥60%          | True        |       39 |     957 |  0.51 | 14/20   |  0.67 |
| 10m       | short_only            | ≥70%          | False       |      204 |     553 |  0.5  | 12/20   |  0.4  |
| 10m       | short_only            | ≥70%          | True        |       42 |     168 |  0.45 | 12/20   |  0.18 |
| 30m       | long_short            | ≥70%          | True        |       39 |      38 |  0.51 | 14/20   |  0.02 |
| 10m       | short_only            | every slot    | True        |       48 |    -103 |  0.42 | 9/20    | -0.14 |
| 10m       | short_only            | ≥60%          | True        |       42 |    -189 |  0.48 | 12/20   | -0.25 |
| 30m       | long_short            | ≥60%          | False       |      233 |    -199 |  0.52 | 12/20   | -0.08 |
| 10m       | long_only             | every slot    | True        |       35 |    -743 |  0.54 | 13/19   | -0.78 |
| 30m       | long_only             | every slot    | True        |       29 |    -781 |  0.66 | 12/19   | -0.45 |
| 30m       | long_short            | every slot    | False       |      240 |    -962 |  0.51 | 9/20    | -0.51 |
| 60m       | long_short            | ≥60%          | True        |       41 |   -1046 |  0.46 | 13/20   | -0.4  |
| 60m       | long_short            | every slot    | True        |       41 |   -1313 |  0.44 | 14/20   | -0.49 |
| 10m       | long_short            | every slot    | False       |      700 |   -1334 |  0.47 | 7/20    | -0.55 |
| 10m       | long_only             | ≥60%          | True        |       42 |   -1574 |  0.43 | 9/18    | -1.58 |
| 30m       | long_short            | ≥70%          | False       |      198 |   -1579 |  0.54 | 11/20   | -0.64 |
| 10m       | long_short            | ≥60%          | False       |      579 |   -1740 |  0.49 | 9/20    | -0.76 |
| 30m       | long_only             | ≥60%          | True        |       30 |   -1753 |  0.57 | 12/18   | -0.92 |
| 10m       | long_short            | ≥60%          | True        |       53 |   -1772 |  0.38 | 9/20    | -1.61 |
| 10m       | long_short            | every slot    | True        |       58 |   -1893 |  0.34 | 9/20    | -1.77 |
| 10m       | long_short            | ≥70%          | True        |       52 |   -1915 |  0.38 | 10/20   | -1.55 |
| 60m       | long_short            | ≥60%          | False       |      119 |   -1923 |  0.51 | 10/20   | -0.51 |
| 10m       | long_only             | ≥70%          | True        |       37 |   -1960 |  0.35 | 6/16    | -1.84 |
| 30m       | long_only             | ≥70%          | True        |       28 |   -2189 |  0.5  | 8/16    | -1.31 |
| 60m       | long_short            | ≥70%          | True        |       44 |   -2367 |  0.43 | 13/20   | -0.83 |
| 60m       | long_only             | every slot    | True        |       38 |   -3175 |  0.39 | 10/18   | -1.4  |
| 30m       | long_only             | ≥60%          | False       |      120 |   -3181 |  0.51 | 10/18   | -1.19 |
| 60m       | long_short            | ≥70%          | False       |      105 |   -3336 |  0.44 | 11/20   | -0.9  |
| 30m       | long_only             | every slot    | False       |      137 |   -3395 |  0.5  | 9/19    | -1.22 |
| 60m       | long_only             | ≥60%          | True        |       33 |   -3701 |  0.39 | 8/16    | -1.62 |
| 60m       | long_only             | ≥70%          | True        |       30 |   -3819 |  0.33 | 7/15    | -1.57 |
| 30m       | long_only             | ≥70%          | False       |       90 |   -3950 |  0.52 | 6/16    | -1.64 |
| 10m       | long_only             | ≥70%          | False       |      130 |   -4046 |  0.41 | 5/16    | -1.93 |
| 10m       | long_only             | ≥60%          | False       |      271 |   -4065 |  0.42 | 7/18    | -1.82 |
| 10m       | long_short            | ≥70%          | False       |      332 |   -4131 |  0.46 | 8/20    | -1.8  |
| 60m       | long_short            | every slot    | False       |      120 |   -4332 |  0.48 | 9/20    | -1.22 |
| 10m       | long_only             | every slot    | False       |      407 |   -4998 |  0.45 | 8/19    | -1.93 |
| 60m       | long_only             | ≥70%          | False       |       51 |   -5606 |  0.31 | 6/15    | -1.8  |
| 60m       | long_only             | every slot    | False       |       77 |   -5924 |  0.38 | 7/18    | -1.9  |
| 60m       | long_only             | ≥60%          | False       |       61 |   -6262 |  0.34 | 5/16    | -2.02 |
| 10m       | BASELINE always long  | every slot    | False       |      720 |   -8087 |  0.46 | 7/20    | -2.15 |
| 30m       | BASELINE always long  | every slot    | False       |      240 |   -8178 |  0.45 | 7/20    | -2.03 |
| 60m       | BASELINE always long  | every slot    | False       |      120 |   -9371 |  0.46 | 8/20    | -2.01 |
