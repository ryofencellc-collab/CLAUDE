# Round 62b: direction study on Yahoo 1-minute data (SPY + market-wide + calendar variables)

Rules: [PROTOCOL_ROUND62.md](../PROTOCOL_ROUND62.md) amendment 5. 100 SPY shares per trade (~$74k), 1¢/share each way. Leave-one-day-out.
Days: **20** (2026-10-23 → 2026-11-19); minutes analysed: 6,920; variables: 52.

- 10-min horizon: best model policy $1,917 vs best no-model baseline $5,207; model ≥60% long/short $-4,234 vs time-shift null 95th pct $2,810.
- 30-min horizon: best model policy $3,579 vs best no-model baseline $7,218; model ≥60% long/short $-313 vs time-shift null 95th pct $4,381.
- 60-min horizon: best model policy $3,575 vs best no-model baseline $8,891; model ≥60% long/short $-1,938 vs time-shift null 95th pct $4,890.

| horizon   | policy                | selectivity   | walk_away   |   trades |   total |   win | green   |     t |
|:----------|:----------------------|:--------------|:------------|---------:|--------:|------:|:--------|------:|
| 60m       | BASELINE always short | every slot    | False       |      120 |    8891 |  0.54 | 12/20   |  1.91 |
| 30m       | BASELINE always short | every slot    | False       |      240 |    7218 |  0.54 | 12/20   |  1.79 |
| 10m       | BASELINE always short | every slot    | False       |      720 |    5207 |  0.52 | 9/20    |  1.39 |
| 30m       | short_only            | every slot    | False       |      178 |    3579 |  0.49 | 12/20   |  1.35 |
| 60m       | short_only            | ≥70%          | False       |       70 |    3575 |  0.59 | 15/19   |  2.14 |
| 60m       | short_only            | every slot    | False       |       86 |    3054 |  0.55 | 11/19   |  1.59 |
| 60m       | short_only            | ≥60%          | False       |       76 |    2927 |  0.58 | 14/19   |  1.87 |
| 60m       | short_only            | every slot    | True        |       35 |    2738 |  0.49 | 13/19   |  1.64 |
| 30m       | short_only            | ≥60%          | False       |      150 |    2630 |  0.55 | 14/20   |  1.5  |
| 60m       | short_only            | ≥70%          | True        |       31 |    2542 |  0.58 | 14/19   |  1.75 |
| 30m       | short_only            | ≥70%          | False       |      122 |    2473 |  0.51 | 12/19   |  1.51 |
| 60m       | short_only            | ≥60%          | True        |       33 |    2177 |  0.52 | 13/19   |  1.47 |
| 10m       | short_only            | every slot    | False       |      490 |    1917 |  0.48 | 9/20    |  0.81 |
| 30m       | short_only            | ≥70%          | True        |       34 |    1733 |  0.53 | 14/19   |  1.52 |
| 30m       | short_only            | every slot    | True        |       46 |    1674 |  0.43 | 15/20   |  1.28 |
| 30m       | short_only            | ≥60%          | True        |       39 |    1236 |  0.51 | 13/20   |  1.07 |
| 30m       | long_short            | every slot    | True        |       40 |    1235 |  0.5  | 13/20   |  0.95 |
| 10m       | short_only            | ≥60%          | False       |      354 |     818 |  0.51 | 11/20   |  0.5  |
| 10m       | short_only            | ≥60%          | True        |       40 |     156 |  0.5  | 12/20   |  0.21 |
| 10m       | short_only            | ≥70%          | False       |      216 |     102 |  0.47 | 13/20   |  0.09 |
| 30m       | long_short            | ≥70%          | True        |       39 |      55 |  0.51 | 15/20   |  0.03 |
| 10m       | short_only            | every slot    | True        |       48 |     -16 |  0.42 | 11/20   | -0.02 |
| 30m       | long_short            | ≥60%          | False       |      233 |    -313 |  0.53 | 11/20   | -0.11 |
| 30m       | long_short            | ≥60%          | True        |       40 |    -486 |  0.5  | 13/20   | -0.26 |
| 10m       | short_only            | ≥70%          | True        |       50 |    -579 |  0.38 | 10/20   | -0.95 |
| 10m       | long_short            | every slot    | True        |       47 |    -830 |  0.43 | 13/20   | -0.77 |
| 30m       | long_only             | ≥60%          | True        |       31 |    -969 |  0.55 | 12/18   | -0.53 |
| 10m       | long_only             | every slot    | True        |       38 |   -1056 |  0.53 | 12/20   | -1.05 |
| 30m       | long_only             | ≥70%          | True        |       31 |   -1087 |  0.45 | 10/16   | -0.63 |
| 60m       | long_short            | ≥60%          | True        |       41 |   -1219 |  0.46 | 13/20   | -0.46 |
| 30m       | long_short            | every slot    | False       |      240 |   -1451 |  0.51 | 8/20    | -0.71 |
| 10m       | long_only             | ≥70%          | True        |       36 |   -1473 |  0.33 | 7/16    | -1.31 |
| 10m       | long_short            | ≥70%          | True        |       55 |   -1490 |  0.36 | 10/20   | -1.3  |
| 30m       | long_only             | every slot    | True        |       40 |   -1524 |  0.48 | 13/19   | -0.84 |
| 60m       | long_short            | ≥70%          | True        |       43 |   -1581 |  0.44 | 12/20   | -0.57 |
| 60m       | long_short            | every slot    | True        |       44 |   -1631 |  0.41 | 13/20   | -0.62 |
| 10m       | long_only             | ≥60%          | True        |       38 |   -1655 |  0.47 | 10/18   | -1.4  |
| 30m       | long_short            | ≥70%          | False       |      197 |   -1848 |  0.49 | 10/20   | -0.65 |
| 10m       | long_short            | ≥60%          | True        |       52 |   -1901 |  0.38 | 9/20    | -1.53 |
| 60m       | long_short            | ≥60%          | False       |      117 |   -1938 |  0.5  | 10/20   | -0.5  |
| 60m       | long_short            | ≥70%          | False       |      106 |   -2164 |  0.47 | 12/20   | -0.59 |
| 10m       | long_short            | every slot    | False       |      700 |   -2826 |  0.47 | 9/20    | -0.96 |
| 30m       | long_only             | ≥70%          | False       |       91 |   -2880 |  0.46 | 8/16    | -1.26 |
| 30m       | long_only             | ≥60%          | False       |      122 |   -2971 |  0.47 | 9/18    | -1.21 |
| 60m       | long_only             | every slot    | True        |       36 |   -3043 |  0.42 | 10/17   | -1.35 |
| 60m       | long_only             | ≥70%          | True        |       28 |   -3589 |  0.36 | 6/14    | -1.53 |
| 60m       | long_only             | ≥60%          | True        |       33 |   -3772 |  0.36 | 8/16    | -1.62 |
| 30m       | long_only             | every slot    | False       |      148 |   -3968 |  0.49 | 10/19   | -1.3  |
| 60m       | long_short            | every slot    | False       |      120 |   -4057 |  0.49 | 9/20    | -1.15 |
| 10m       | long_only             | ≥70%          | False       |      116 |   -4174 |  0.35 | 4/16    | -1.96 |
| 10m       | long_short            | ≥60%          | False       |      570 |   -4234 |  0.47 | 8/20    | -1.91 |
| 10m       | long_short            | ≥70%          | False       |      330 |   -4408 |  0.43 | 7/20    | -2.05 |
| 10m       | long_only             | ≥60%          | False       |      254 |   -5385 |  0.43 | 5/18    | -2.17 |
| 60m       | long_only             | ≥70%          | False       |       48 |   -5538 |  0.29 | 4/14    | -1.86 |
| 60m       | long_only             | every slot    | False       |       74 |   -5805 |  0.38 | 8/17    | -1.86 |
| 10m       | long_only             | every slot    | False       |      409 |   -6066 |  0.44 | 8/20    | -2.14 |
| 60m       | long_only             | ≥60%          | False       |       63 |   -6260 |  0.3  | 5/16    | -2    |
| 10m       | BASELINE always long  | every slot    | False       |      720 |   -8087 |  0.46 | 7/20    | -2.15 |
| 30m       | BASELINE always long  | every slot    | False       |      240 |   -8178 |  0.45 | 7/20    | -2.03 |
| 60m       | BASELINE always long  | every slot    | False       |      120 |   -9371 |  0.46 | 8/20    | -2.01 |
