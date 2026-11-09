# Round 39a: 0DTE implied move (VIX1D) vs realized move — model screen

SPX + VIX1D 2022-05-13 → 2026-11-06, 1126 days; dev < 2024-08-12 ≤ holdout.
Units: SPX index points per 1-lot (×$100). Cost 0.6 pt. Median premium (A) 32.0 pt.

| test                                   | part    |    n |   mean |    t |   win |   worst |   total |
|:---------------------------------------|:--------|-----:|-------:|-----:|------:|--------:|--------:|
| A straddle open→close                  | dev     |  563 |  3.999 | 4.25 | 0.622 |  -93.01 |  2251.2 |
| A straddle open→close                  | holdout |  563 |  2.376 | 1.7  | 0.616 | -329.63 |  1337.5 |
| A straddle open→close                  | all     | 1126 |  3.187 | 3.78 | 0.619 | -329.63 |  3588.7 |
| B straddle close→close                 | dev     |  562 |  1.952 | 1.72 | 0.614 | -130.91 |  1096.8 |
| B straddle close→close                 | holdout |  563 |  4.716 | 2.7  | 0.639 | -290.48 |  2655   |
| B straddle close→close                 | all     | 1125 |  3.335 | 3.2  | 0.627 | -290.48 |  3751.8 |
| C strangle ±1σ open→close (optimistic) | dev     |  563 |  1.961 | 4.18 | 0.815 |  -70.12 |  1103.8 |
| C strangle ±1σ open→close (optimistic) | holdout |  563 |  0.957 | 1.01 | 0.828 | -264.76 |   539   |
| C strangle ±1σ open→close (optimistic) | all     | 1126 |  1.459 | 2.76 | 0.821 | -264.76 |  1642.8 |

## By year (mean pts, days)

|   Date |   ('A', 'mean') |   ('A', 'count') |   ('B', 'mean') |   ('B', 'count') |
|-------:|----------------:|-----------------:|----------------:|-----------------:|
|   2022 |            8.26 |              160 |            0.14 |              159 |
|   2023 |            2.54 |              250 |            3.87 |              250 |
|   2024 |            1.83 |              252 |            1.91 |              252 |
|   2025 |            0.94 |              250 |            4.78 |              250 |
|   2026 |            4.36 |              214 |            5.08 |              214 |

**Pass:** A fail, B fail (model screen only).
