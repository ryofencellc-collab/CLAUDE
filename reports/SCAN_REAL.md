# Segment scanner on real S&P and Nasdaq data

Tests: 534 across 2 sources; Bonferroni |t| ≥ 3.91, same sign both periods (2012–2020 and 2021+).

Significant per source: SP **0**, NQ **0**

Nothing significant. Top 15 by |t|:

| source   | signal        | target      |   mean_bp_dev |   t_dev |   mean_bp_ho |   t_ho |   t_all |
|:---------|:--------------|:------------|---------------:|---------:|---------------:|---------:|--------:|
| NQ       | weekday1      | 14:00→15:00 |           2.29 |     1.67 |           4.89 |     2.39 |    2.79 |
| NQ       | open→15:00    | 15:00→close |           0.8  |     1.04 |           3.2  |     3.14 |    2.76 |
| NQ       | weekday0      | open→close  |           7.35 |     1.69 |          14.06 |     2.25 |    2.72 |
| NQ       | overnight/gap | open→09:45  |          -0.93 |    -1.9  |          -1.89 |    -1.95 |   -2.7  |
| NQ       | weekday0      | open→09:45  |           1.11 |     1.02 |           4.53 |     3    |    2.66 |
| NQ       | weekday0      | open→15:00  |           5.78 |     1.52 |          13.26 |     2.28 |    2.61 |
| NQ       | weekday0      | 10:30→close |           8.56 |     2.01 |           9.18 |     1.58 |    2.55 |
| SP       | weekday1      | 14:00→15:00 |           3.45 |     1.29 |           3.5  |     2.2  |    2.53 |
| NQ       | weekday0      | 10:30→15:00 |           6.97 |     1.96 |           8.38 |     1.55 |    2.5  |
| NQ       | open→12:00    | 15:00→close |           0.93 |     1.21 |           2.56 |     2.5  |    2.5  |
| NQ       | weekday0      | 10:00→close |           6.88 |     1.64 |           9.21 |     1.58 |    2.27 |
| NQ       | weekday0      | open→14:00  |           4.02 |     1.12 |          11.42 |     2.17 |    2.22 |
| NQ       | weekday0      | 10:00→15:00 |           5.29 |     1.49 |           8.41 |     1.56 |    2.14 |
| NQ       | weekday0      | 09:45→close |           6.23 |     1.49 |           9.55 |     1.53 |    2.12 |
| NQ       | weekday0      | 10:30→14:00 |           5.21 |     1.58 |           6.54 |     1.38 |    2.09 |

Columns: *_dev = 2012–2020 (S&P from its first file), *_ho = 2021 → now. mean_bp = basis points per day before costs; a micro round trip costs about 1–2 bp.
