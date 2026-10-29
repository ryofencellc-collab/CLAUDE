# Round 20 SMOKE TEST: blind 98-99c maker bids on Kalshi favorites

Rules: [PROTOCOL_ROUND20.md](../PROTOCOL_ROUND20.md). Window 2026-09-23 to 2026-09-29.

## Verdict: **FAIL** (smoke)

| | |
|---|---|
| Long-shot fills | 9,103 (25 long shots won) |
| Net profit at 25% capture | **$12,522.80** (100%: $50,281.04) |
| Days | 7 (profitable 100%); average $1,788.97/day |
| Worst day | $327.60 |
| Last 60 days | $12,522.80 |

| Check | Result |
|---|---|
| net profit >= $6,000 | yes |
| profitable on >= 80% of days | yes |
| worst day >= -$300 | yes |
| last 60 days >= 20% of total | yes |

## Per series

| series     |   fills |   contracts |   longshot_wins |   net_25 |   net_100 |   median_min_to_close |
|:-----------|--------:|------------:|----------------:|---------:|----------:|----------------------:|
| KXWTAMATCH |    9103 | 4.21422e+06 |              25 |  12522.8 |     50281 |                     9 |

## By minutes to close

| min_to_close   |   fills |   longshot_wins |   net_25 |
|:---------------|--------:|----------------:|---------:|
| <1m            |    1386 |               0 |  1431.06 |
| 1-5m           |    2036 |               0 |  2566.9  |
| 5-15m          |    3225 |               0 |  6256.62 |
| 15-60m         |    2390 |               0 |  3561.83 |
| 1-4h           |      66 |              25 | -1293.62 |
| >4h            |       0 |               0 |     0    |

## Worst 15 fills

| series     | ticker                       | time                             |   px |   count |     pnl |   min_to_close |
|:-----------|:-----------------------------|:---------------------------------|-----:|--------:|--------:|---------------:|
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-EAL | 2026-09-24 12:26:16.061934+00:00 | 0.02 | 2139.43 | -524.35 |          83.93 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-EAL | 2026-09-24 12:26:16.061934+00:00 | 0.02 |  816.6  | -200.15 |          83.93 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-EAL | 2026-09-24 12:26:52.259239+00:00 | 0.02 |  500    | -122.55 |          83.33 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-PRO | 2026-09-24 12:25:37.806471+00:00 | 0.02 |  312.13 |  -76.5  |          84.57 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-EAL | 2026-09-24 12:25:30.908101+00:00 | 0.02 |  250    |  -61.28 |          84.68 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-EAL | 2026-09-24 12:25:32.035758+00:00 | 0.02 |  242.22 |  -59.37 |          84.67 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-PRO | 2026-09-24 12:25:51.282458+00:00 | 0.02 |  233.94 |  -57.35 |          84.35 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-PRO | 2026-09-24 12:26:16.060484+00:00 | 0.02 |  171.84 |  -42.12 |          83.93 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-PRO | 2026-09-24 12:25:57.347407+00:00 | 0.02 |  166.06 |  -40.7  |          84.24 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-PRO | 2026-09-24 12:25:57.352177+00:00 | 0.02 |  156.27 |  -38.31 |          84.24 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-EAL | 2026-09-24 12:25:32.035758+00:00 | 0.02 |  100.35 |  -24.6  |          84.67 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-PRO | 2026-09-24 12:25:31.396793+00:00 | 0.02 |   93.58 |  -22.94 |          84.68 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-PRO | 2026-09-24 12:26:16.060484+00:00 | 0.02 |   93    |  -22.8  |          83.93 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-EAL | 2026-09-24 12:25:49.295046+00:00 | 0.02 |   71.67 |  -17.57 |          84.38 |
| KXWTAMATCH | KXWTAMATCH-26SEP22PROEAL-PRO | 2026-09-24 12:26:15.466019+00:00 | 0.02 |   71    |  -17.4  |          83.94 |
