# Round 21 live paper test: 99c bids on crypto markets decided by the spot price

Updated 2026-11-06 04:24 UTC. Rules: [PROTOCOL_ROUND21.md](../PROTOCOL_ROUND21.md), "Forward test". 1,000 contracts per market at z >= 6; fills only after the live queue ahead.

| | |
|---|---|
| Markets bid and settled | 112,674 (cancelled before close 2,896); open now 795 |
| Markets that got any fill | 476 (0.4%) |
| Losing filled markets | 3 |
| Contracts filled | 151,548 |
| **Paper profit** | **$+1,483.08** |
| Average queue ahead at placement | 19,209 contracts |

| Day | Settled | Filled markets | Contracts | P&L |
|---|---:|---:|---:|---:|
| 2026-10-29 | 3,653 | 8 | 8,000 | $+78.56 |
| 2026-10-30 | 15,338 | 34 | 4,133 | $+40.36 |
| 2026-10-31 | 13,839 | 61 | 22,150 | $+217.32 |
| 2026-11-01 | 14,488 | 60 | 20,896 | $+204.95 |
| 2026-11-02 | 10,066 | 50 | 15,999 | $+156.89 |
| 2026-11-03 | 19,565 | 65 | 21,296 | $+208.85 |
| 2026-11-04 | 13,197 | 55 | 23,770 | $+233.26 |
| 2026-11-05 | 18,252 | 142 | 35,255 | $+342.42 |
| 2026-11-06 | 4,276 | 1 | 48 | $+0.47 |

| Series | Settled | Filled markets | Contracts | P&L | Avg queue |
|---|---:|---:|---:|---:|---:|
| KXBTC15M | 101 | 12 | 12,000 | $+117.84 | 569,120 |
| KXBTCD | 23,328 | 55 | 32,389 | $+317.97 | 18,492 |
| KXDOGE15M | 76 | 15 | 15,000 | $+147.30 | 24,450 |
| KXETH15M | 84 | 3 | 3,000 | $+29.46 | 82,070 |
| KXETHD | 37,263 | 47 | 10,123 | $+99.21 | 20,203 |
| KXINX | 87 | 10 | 2,384 | $+23.36 | 1,047 |
| KXINXU | 1,631 | 104 | 10,912 | $+103.47 | 5,721 |
| KXNASDAQ100 | 87 | 2 | 1,009 | $+9.90 | 675 |
| KXNASDAQ100U | 3,163 | 21 | 1,832 | $+17.83 | 5,300 |
| KXSOL15M | 85 | 14 | 14,000 | $+137.48 | 34,003 |
| KXSOLD | 37,187 | 71 | 9,433 | $+92.37 | 18,923 |
| KXXRP15M | 97 | 25 | 24,147 | $+237.12 | 33,381 |
| KXXRPD | 9,485 | 97 | 15,319 | $+149.77 | 18,752 |

## Capital a real account would tie up (resting bids x size x 99c)

| Day | Group | Average | Peak |
|---|---|---:|---:|
| 2026-11-02 | crypto15m | $270 | $39,600 |
| 2026-11-02 | crypto_hourly | $655,343 | $839,520 |
| 2026-11-02 | index | $0 | $0 |
| 2026-11-03 | crypto15m | $714 | $49,500 |
| 2026-11-03 | crypto_hourly | $746,115 | $846,450 |
| 2026-11-03 | index | $17,088 | $498,960 |
| 2026-11-04 | crypto15m | $1,123 | $49,500 |
| 2026-11-04 | crypto_hourly | $697,580 | $842,490 |
| 2026-11-04 | index | $20,881 | $505,890 |
| 2026-11-05 | crypto15m | $768 | $49,500 |
| 2026-11-05 | crypto_hourly | $559,370 | $838,530 |
| 2026-11-05 | index | $29,315 | $480,150 |
| 2026-11-06 | crypto15m | $705 | $39,600 |
| 2026-11-06 | crypto_hourly | $756,289 | $830,610 |
| 2026-11-06 | index | $0 | $0 |

## Round 24 forward test (S&P 500 / Nasdaq-100 binaries), 2026-11-02 to 2026-11-15

| | |
|---|---|
| Paper profit | **$+154.56** |
| Markets settled / filled | 4,968 / 137 |
| Losing filled markets | 3 |
| Days with fills | 4 (green 100%) |

## Round 22 sizing (10k contracts on 15-minute markets), window 2026-10-31 to 2026-11-13

| | |
|---|---|
| Paper profit at Round 22 size | **$+5,566.61** |
| Losing filled markets | 3 |
| Days with fills | 7 (green 100%) |
| Worst day | $+0.47 |

Filled or wrong markets are listed in [r21_fills.csv](r21_fills.csv) (523 rows).
