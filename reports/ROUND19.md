# Round 19: Round 18 trade on other daily-temperature series

Rules: [PROTOCOL_ROUND19.md](../PROTOCOL_ROUND19.md). Window 2025-10-28 to 2026-10-27.

## Verdict: **PASS**

| | |
|---|---|
| Series scanned | 29 (eligible after dev screen: 22) |
| Holdout decided markets | 4,059, right 99.98% |
| Holdout profit at 25% capture | **$2,696.92** (100%: $11,470.28) |
| Holdout days with an opportunity | 183 (profitable 99%) |
| Average per opportunity day (25%) | $14.74 |
| Last 3 months (25%) | $1,109.88 |

| Check | Result |
|---|---|
| holdout decided calls >= 99.5% right | yes |
| holdout profit at 25% capture >= $1,000 | yes |
| profitable on >= 60% of opportunity days | yes |
| opportunities on >= 50 days | yes |
| last 3 months >= 30% of holdout total | yes |

## Per series

| series      | kind   |   decided |   right |   dev_decided |   dev_right | eligible   |   holdout_profit_25 |
|:------------|:-------|----------:|--------:|--------------:|------------:|:-----------|--------------------:|
| KXLOWTNYC   | low    |       428 |   1     |           152 |       1     | True       |             474.924 |
| KXLOWTDEN   | low    |       769 |   1     |           406 |       1     | True       |             326.816 |
| KXHIGHTDAL  | high   |       301 |   1     |            91 |       1     | True       |             271.017 |
| KXLOWTMIA   | low    |       346 |   1     |           123 |       1     | True       |             257.768 |
| KXHIGHTSEA  | high   |       400 |   1     |           168 |       1     | True       |             233.35  |
| KXLOWTAUS   | low    |       600 |   1     |           278 |       1     | True       |             176.358 |
| KXHIGHTLV   | high   |       382 |   1     |           131 |       1     | True       |             155.314 |
| KXLOWTCHI   | low    |       327 |   1     |           164 |       1     | True       |             126.386 |
| KXLOWTOKC   | low    |       259 |   1     |            29 |       1     | True       |             105.788 |
| KXLOWTNOLA  | low    |       266 |   1     |            28 |       1     | True       |              87.134 |
| KXLOWTDAL   | low    |       179 |   1     |            21 |       1     | True       |              81.389 |
| KXLOWTLAX   | low    |       183 |   1     |           103 |       1     | True       |              67.396 |
| KXLOWTATL   | low    |       143 |   1     |            13 |       1     | True       |              56.216 |
| KXHIGHTSATX | high   |       265 |   1     |           108 |       1     | True       |              53.803 |
| KXLOWTSEA   | low    |       141 |   1     |            16 |       1     | True       |              44.388 |
| KXLOWTSATX  | low    |       195 |   1     |            24 |       1     | True       |              43.418 |
| KXLOWTSFO   | low    |       215 |   1     |            26 |       1     | True       |              40.647 |
| KXLOWTDC    | low    |       165 |   1     |            30 |       1     | True       |              34.924 |
| KXLOWTBOS   | low    |       171 |   1     |            29 |       1     | True       |              29.648 |
| KXLOWTLV    | low    |        71 |   1     |            10 |       1     | True       |              16.068 |
| KXLOWTPHIL  | low    |       169 |   1     |            96 |       1     | True       |              14.375 |
| KXLOWTMIN   | low    |       160 |   0.994 |            30 |       1     | True       |              -0.205 |
| KXHIGHTBOS  | high   |       400 |   0.998 |           132 |       0.992 | False      |             nan     |
| KXHIGHTEWR  | high   |        92 |   1     |           nan |     nan     | False      |             nan     |
| KXLOWTEWR   | low    |        68 |   1     |           nan |     nan     | False      |             nan     |
| KXLOWTHOU   | low    |       222 |   0.991 |            26 |       0.923 | False      |             nan     |
| KXLOWTPHX   | low    |       106 |   1     |             4 |       1     | False      |             nan     |
| KXLOWTSAN   | low    |        65 |   1     |           nan |     nan     | False      |             nan     |
| KXLOWTTTN   | low    |        59 |   1     |           nan |     nan     | False      |             nan     |

## Decided calls that settled the other way (4)

| series     | date                | ticker                   | side   | result   |   floor |   cap |
|:-----------|:--------------------|:-------------------------|:-------|:---------|--------:|------:|
| KXLOWTHOU  | 2026-04-23 00:00:00 | KXLOWTHOU-26APR23-T63    | yes    | no       |     nan |    63 |
| KXLOWTHOU  | 2026-04-23 00:00:00 | KXLOWTHOU-26APR23-B69.5  | no     | yes      |      69 |    70 |
| KXHIGHTBOS | 2026-04-20 00:00:00 | KXHIGHTBOS-26APR20-B52.5 | no     | yes      |      52 |    53 |
| KXLOWTMIN  | 2026-05-12 00:00:00 | KXLOWTMIN-26MAY12-B55.5  | no     | yes      |      55 |    56 |
