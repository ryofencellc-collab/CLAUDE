# Blind test: results

Rules: [PROTOCOL_BLIND.md](../PROTOCOL_BLIND.md). Commitment sha256 `a7ddf612…421df`.

## Guess (written before the reveal)
- **Source: X.** Y and Z produce **zero** candidates on both detectors, so there are no false positives.
- **Strategy: opening-range breakout continuation with a 15-minute range.** All 16 grid candidates are ORB15; ORB5, ORB30 and ORB60
  produce none. The scanner's strongest signal is "direction of open→10:00 predicts 10:00→close", and filter "none" beats every filter.
- Narrow-range breakout is second most likely, because the low_vol filter also appears. It is rejected because unfiltered beats filtered.

## Detector 1: Round 53 grid (unchanged system)

Configurations: 5184 (1728 per source). Dev 2024, holdout 2025.

Screen candidates per source: X **16**, Y **0**, Z **0**

Configs with t ≥ 2 in BOTH years, per source: X 91, Y 0, Z 0

Candidates by source and entry family:

| source   | entry   |   n |
|:---------|:--------|----:|
| X        | ORB15   |  16 |

Top 15 candidates:

| source   | entry   | stop      | target   | exit   | filter   |   dev_n |   dev_meanR |   dev_t |   ho_n |   ho_meanR |   ho_t |
|:---------|:--------|:----------|:---------|:-------|:---------|--------:|------------:|--------:|-------:|-----------:|-------:|
| X        | ORB15   | structure | 2R       | 15:55  | none     |     260 |       0.447 |   5.832 |    261 |      0.326 |  4.14  |
| X        | ORB15   | structure | 3R       | 15:55  | none     |     260 |       0.533 |   5.903 |    261 |      0.368 |  4.105 |
| X        | ORB15   | 0.5%      | 2R       | 15:55  | none     |     260 |       0.405 |   5.278 |    261 |      0.318 |  4.084 |
| X        | ORB15   | 0.5%      | 3R       | 15:55  | none     |     260 |       0.486 |   5.533 |    261 |      0.364 |  4.058 |
| X        | ORB15   | 0.5%      | time     | 15:55  | none     |     260 |       0.505 |   5.272 |    261 |      0.425 |  3.969 |
| X        | ORB15   | structure | time     | 15:55  | none     |     260 |       0.555 |   5.685 |    261 |      0.36  |  3.897 |
| X        | ORB15   | 0.5%      | 2R       | 15:55  | low_vol  |     104 |       0.37  |   3.247 |    133 |      0.379 |  3.806 |
| X        | ORB15   | 0.5%      | 3R       | 15:55  | low_vol  |     104 |       0.376 |   3.104 |    133 |      0.412 |  3.793 |
| X        | ORB15   | 0.25%     | time     | 15:55  | none     |     260 |       0.726 |   4.374 |    261 |      0.707 |  3.679 |
| X        | ORB15   | 0.5%      | 1R       | 15:55  | low_vol  |     104 |       0.191 |   2.208 |    133 |      0.264 |  3.599 |
| X        | ORB15   | 0.5%      | time     | 15:55  | low_vol  |     104 |       0.352 |   2.987 |    133 |      0.412 |  3.527 |
| X        | ORB15   | 0.25%     | 3R       | 15:55  | none     |     260 |       0.504 |   4.419 |    261 |      0.398 |  3.508 |
| X        | ORB15   | 0.5%      | 1R       | 15:55  | none     |     260 |       0.235 |   4.222 |    261 |      0.193 |  3.408 |
| X        | ORB15   | structure | 1R       | 15:55  | none     |     260 |       0.254 |   4.585 |    261 |      0.192 |  3.357 |
| X        | ORB15   | structure | 2R       | 15:55  | low_vol  |     104 |       0.363 |   2.823 |    133 |      0.346 |  3.14  |

Top 15 by the weaker of the two years' t:

| source   | entry   | stop      | target   | exit   | filter   |   dev_t |   ho_t |   ho_meanR |
|:---------|:--------|:----------|:---------|:-------|:---------|--------:|-------:|-----------:|
| X        | ORB15   | structure | 2R       | 15:55  | none     |    5.83 |   4.14 |       0.33 |
| X        | ORB15   | structure | 3R       | 15:55  | none     |    5.9  |   4.11 |       0.37 |
| X        | ORB15   | 0.5%      | 2R       | 15:55  | none     |    5.28 |   4.08 |       0.32 |
| X        | ORB15   | 0.5%      | 3R       | 15:55  | none     |    5.53 |   4.06 |       0.36 |
| X        | ORB15   | 0.5%      | time     | 15:55  | none     |    5.27 |   3.97 |       0.43 |
| X        | ORB15   | structure | time     | 15:55  | none     |    5.69 |   3.9  |       0.36 |
| X        | ORB15   | 0.25%     | time     | 15:55  | none     |    4.37 |   3.68 |       0.71 |
| X        | ORB15   | 0.25%     | 3R       | 15:55  | none     |    4.42 |   3.51 |       0.4  |
| X        | ORB15   | 0.5%      | 1R       | 15:55  | none     |    4.22 |   3.41 |       0.19 |
| X        | ORB15   | structure | 1R       | 15:55  | none     |    4.58 |   3.36 |       0.19 |
| X        | ORB15   | 0.5%      | 2R       | 15:55  | low_vol  |    3.25 |   3.81 |       0.38 |
| X        | ORB15   | 0.5%      | 3R       | 15:55  | low_vol  |    3.1  |   3.79 |       0.41 |
| X        | ORB15   | 0.25%     | 2R       | 15:55  | none     |    3.77 |   2.99 |       0.27 |
| X        | ORB15   | 0.5%      | time     | 15:55  | low_vol  |    2.99 |   3.53 |       0.41 |
| X        | ORB15   | 0.25%     | time     | 11:30  | none     |    3.52 |   2.88 |       0.35 |
## Detector 2: generic segment scanner

Tests: 801 across 3 sources; Bonferroni |t| ≥ 4.00, same sign both years.

Significant per source: X **22**, Y **0**, Z **0**

Significant tests:

| source   | signal     | target      |   mean_bp_2024 |   t_2024 |   mean_bp_2025 |   t_2025 |   t_all |
|:---------|:-----------|:------------|---------------:|---------:|---------------:|---------:|--------:|
| X        | open→10:00 | 10:00→close |          27.27 |     4.73 |          22.33 |     3.66 |    5.93 |
| X        | open→10:00 | 10:00→15:00 |          21.17 |     4.3  |          19.78 |     3.6  |    5.58 |
| X        | open→12:00 | 12:00→close |          20    |     4.43 |          14.54 |     3.13 |    5.35 |
| X        | open→12:00 | 12:00→15:00 |          14.03 |     4.08 |          11.89 |     3.34 |    5.25 |
| X        | open→10:00 | 10:30→close |          23.88 |     4.45 |          16.71 |     2.91 |    5.2  |
| X        | open→09:45 | 10:00→close |          23.39 |     4.01 |          19.32 |     3.15 |    5.06 |
| X        | open→10:00 | 10:00→14:00 |          17.76 |     4.11 |          14.32 |     2.88 |    4.94 |
| X        | open→09:45 | 09:45→close |          24.79 |     3.83 |          21.07 |     3.11 |    4.91 |
| X        | open→10:00 | 10:30→15:00 |          17.75 |     3.91 |          14.17 |     2.76 |    4.71 |
| X        | open→09:45 | 10:30→close |          21.13 |     3.91 |          15.25 |     2.64 |    4.63 |
| X        | open→09:45 | 10:00→15:00 |          17.77 |     3.57 |          15.63 |     2.82 |    4.52 |
| X        | open→10:00 | 12:00→close |          18.49 |     4.08 |          10.57 |     2.26 |    4.48 |
| X        | open→09:45 | 09:45→15:00 |          19.17 |     3.42 |          17.4  |     2.81 |    4.4  |
| X        | open→12:00 | 14:00→close |          12.69 |     3.87 |           8.36 |     2.28 |    4.34 |
| X        | open→10:00 | 10:00→12:00 |           8.81 |     2.94 |          11.78 |     3.15 |    4.3  |
## Reveal

sha256 = `a7ddf61213c9b76403cc865b43d1f4582c9a8ac75163704c1f3209a4b42421df`

```json
{"or_minutes": 15, "source": "X", "strategy": "orb_continuation", "strength_k": 0.446}
```

