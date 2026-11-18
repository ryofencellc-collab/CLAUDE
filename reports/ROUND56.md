# Round 56: mega-search of intraday combinations

Rules: [PROTOCOL_ROUND56.md](../PROTOCOL_ROUND56.md). Markets: SP, NQ, GOLD, SILVER, OIL, BRENT, EURUSD, USDJPY, GBPUSD, AUDUSD, USDCAD, DAX, FTSE, NIKKEI.

Configurations tested: **11,916,800**. Survived search (t ≥ 2) and selection (t ≥ 2): **114**. Shortlisted: 20. **Passed the final exam (2023 → now, t ≥ 2.81, n ≥ 100): 0**.

Expected survivors from luck alone if nothing were real: about N × 0.023 × 0.023 × ½ ≈ 3,152 (rough; configurations are correlated).

## Shortlist and final exam

| market   | entry   | signal   | mode   | filter    |   hold |   stop |   search_n |   search_bp |   search_t |   select_n |   select_bp |   select_t |   final_n |   final_bp |   final_t | PASS   |
|:---------|:--------|:---------|:-------|:----------|-------:|-------:|-----------:|------------:|-----------:|-----------:|------------:|-----------:|----------:|-----------:|----------:|:-------|
| NIKKEI   | 11:00   | gap      | rev    | gap_up    |    999 |   0    |         72 |       27.08 |       3.01 |        178 |       14.31 |       3.07 |       380 |      -1.96 |     -0.89 | False  |
| NIKKEI   | 09:40   | prev_20d | rev    | trend_up  |    240 |   0.01 |         40 |       46.7  |       2.99 |        169 |       16.41 |       3.59 |       476 |      -2.93 |     -1.11 | False  |
| NIKKEI   | 10:10   | prev_20d | rev    | trend_up  |    240 |   0.01 |         40 |       38.21 |       2.99 |        169 |       13.11 |       3    |       476 |      -2.82 |     -1.1  | False  |
| NIKKEI   | 09:35   | prev_20d | rev    | trend_up  |    240 |   0    |         40 |       47.53 |       2.98 |        169 |       15.4  |       3.18 |       476 |      -3.16 |     -1.19 | False  |
| NIKKEI   | 10:55   | gap      | rev    | gap_up    |    240 |   0    |         72 |       25.33 |       3    |        178 |       13.04 |       2.89 |       380 |      -0.75 |     -0.28 | False  |
| OIL      | 12:55   | last60   | mom    | gap_up    |    999 |   0    |        733 |        9.18 |       3.3  |        370 |       14.2  |       2.73 |       118 |       7.6  |      0.97 | False  |
| BRENT    | 12:55   | last60   | mom    | trend_up  |    240 |   0.01 |        656 |        7.53 |       2.65 |        431 |       10.21 |       2.49 |       412 |      -3.37 |     -0.9  | False  |
| NQ       | 09:50   | last15   | rev    | lo_range  |    240 |   0    |        913 |        4.05 |       2.48 |        352 |       11.16 |       2.68 |       414 |       1.35 |      0.47 | False  |
| SP       | 12:45   | last15   | rev    | wed       |    240 |   0    |        124 |       14.12 |       2.64 |        152 |       12.58 |       2.45 |       172 |       0.7  |      0.14 | False  |
| SP       | 11:20   | last15   | mom    | trend_dn  |    240 |   0    |        204 |       13.27 |       2.56 |        260 |       14.73 |       2.45 |       247 |      -2.29 |     -0.45 | False  |
| OIL      | 12:15   | last15   | mom    | mon       |    999 |   0    |        261 |       17.17 |       2.87 |        133 |       25.29 |       2.44 |        38 |      -1.04 |     -0.07 | False  |
| NQ       | 11:00   | last30   | mom    | big_q75   |    999 |   0    |        449 |        7.78 |       2.45 |        229 |       15.08 |       2.41 |       193 |      -5.04 |     -1.15 | False  |
| OIL      | 13:05   | last60   | mom    | gap_up    |    240 |   0    |        724 |        6.36 |       2.35 |        367 |       12.88 |       2.38 |       118 |      13.36 |      1.77 | False  |
| NQ       | 15:20   | last30   | mom    | thu       |     60 |   0.01 |        386 |        2.96 |       2.34 |        152 |        7.98 |       2.53 |       163 |      -2.25 |     -1.07 | False  |
| BRENT    | 12:30   | last15   | mom    | wed       |    999 |   0    |        286 |       13.08 |       2.5  |        152 |       17.76 |       2.31 |       169 |       5.76 |      1.02 | False  |
| GOLD     | 13:25   | last30   | rev    | big_q90   |    120 |   0    |        181 |        5.71 |       2.3  |         91 |        9.2  |       2.64 |       102 |      -0.09 |     -0.02 | False  |
| OIL      | 11:20   | last15   | mom    | mon       |    240 |   0.01 |        257 |       17.58 |       2.4  |        134 |       27.43 |       2.29 |        38 |      23.29 |      1.22 | False  |
| SP       | 15:30   | last30   | mom    | month_end |    999 |   0    |        168 |        4.63 |       2.5  |        108 |        7.23 |       2.29 |       125 |      -0.62 |     -0.32 | False  |
| SP       | 15:25   | last60   | mom    | thu       |     30 |   0.01 |        138 |        4.78 |       2.28 |        150 |        5.87 |       2.32 |       167 |      -0.8  |     -0.58 | False  |
| SP       | 10:50   | prev_5d  | rev    | gap_up    |    999 |   0    |        335 |        6.21 |       2.26 |        385 |        8.02 |       2.56 |       465 |      -2.1  |     -1.17 | False  |

## Per market

| market   |   configs |   search_days |   select_days |   final_days |   search_t2 |
|:---------|----------:|--------------:|--------------:|-------------:|------------:|
| AUDUSD   |    851200 |          1812 |           745 |          846 |         214 |
| BRENT    |    851200 |          1390 |           728 |          827 |        3979 |
| DAX      |    851200 |          1829 |           313 |          718 |        1066 |
| EURUSD   |    851200 |          2008 |           768 |          854 |         147 |
| FTSE     |    851200 |          1197 |           703 |          790 |        1775 |
| GBPUSD   |    851200 |          2022 |           770 |          855 |          30 |
| GOLD     |    851200 |          1993 |           750 |          831 |         110 |
| NIKKEI   |    851200 |           134 |           347 |          748 |        5179 |
| NQ       |    851200 |          1890 |           747 |          826 |        1730 |
| OIL      |    851200 |          1465 |           718 |          208 |        2813 |
| SILVER   |    851200 |          1136 |           708 |          833 |        1112 |
| SP       |    851200 |           598 |           735 |          838 |        6694 |
| USDCAD   |    851200 |          1920 |           766 |          856 |          51 |
| USDJPY   |    851200 |          1853 |           701 |          851 |         229 |

