# Round 21 live paper test: 99c bids on crypto markets decided by the spot price

Updated 2026-11-09 14:51 UTC. Rules: [PROTOCOL_ROUND21.md](../PROTOCOL_ROUND21.md), "Forward test". 1,000 contracts per market at z >= 6; fills only after the live queue ahead.

| | |
|---|---|
| Markets bid and settled | 182,997 (cancelled before close 4,013); open now 815 |
| Markets that got any fill | 783 (0.4%) |
| Losing filled markets | 9 |
| Contracts filled | 265,602 |
| **Paper profit** | **$-1,665.26** |
| Average queue ahead at placement | 19,715 contracts |

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
| 2026-11-06 | 21,747 | 90 | 31,860 | $+312.51 |
| 2026-11-07 | 20,071 | 88 | 31,191 | $+305.93 |
| 2026-11-08 | 20,023 | 108 | 42,963 | $-3845.67 |
| 2026-11-09 | 12,758 | 22 | 8,088 | $+79.36 |

| Series | Settled | Filled markets | Contracts | P&L | Avg queue |
|---|---:|---:|---:|---:|---:|
| KXBTC15M | 152 | 25 | 25,000 | $+245.50 | 578,842 |
| KXBTCD | 38,121 | 144 | 82,783 | $-3449.56 | 18,607 |
| KXDOGE15M | 120 | 20 | 20,000 | $+196.40 | 26,111 |
| KXETH15M | 123 | 10 | 10,000 | $+98.20 | 85,847 |
| KXETHD | 60,909 | 87 | 17,954 | $+175.89 | 20,482 |
| KXINX | 116 | 11 | 2,422 | $+23.73 | 1,273 |
| KXINXU | 2,335 | 135 | 16,397 | $+157.20 | 4,933 |
| KXNASDAQ100 | 117 | 2 | 1,009 | $+9.90 | 1,287 |
| KXNASDAQ100U | 4,280 | 31 | 2,867 | $+27.93 | 5,277 |
| KXSOL15M | 160 | 19 | 18,880 | $+185.40 | 39,558 |
| KXSOLD | 60,905 | 114 | 15,446 | $+151.23 | 19,569 |
| KXXRP15M | 162 | 37 | 35,907 | $+352.61 | 37,127 |
| KXXRPD | 15,497 | 148 | 16,937 | $+160.31 | 20,051 |

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
| 2026-11-06 | crypto15m | $585 | $49,500 |
| 2026-11-06 | crypto_hourly | $739,934 | $848,430 |
| 2026-11-06 | index | $22,187 | $625,680 |
| 2026-11-07 | crypto15m | $661 | $49,500 |
| 2026-11-07 | crypto_hourly | $788,817 | $850,410 |
| 2026-11-07 | index | $0 | $0 |
| 2026-11-08 | crypto15m | $729 | $49,500 |
| 2026-11-08 | crypto_hourly | $760,649 | $849,420 |
| 2026-11-08 | index | $0 | $0 |
| 2026-11-09 | crypto15m | $491 | $39,600 |
| 2026-11-09 | crypto_hourly | $758,942 | $834,570 |
| 2026-11-09 | index | $0 | $0 |

## Round 24 forward test (S&P 500 / Nasdaq-100 binaries), 2026-11-02 to 2026-11-15

| | |
|---|---|
| Paper profit | **$+218.76** |
| Markets settled / filled | 6,848 / 179 |
| Losing filled markets | 3 |
| Days with fills | 5 (green 100%) |

## Round 22 sizing (10k contracts on 15-minute markets), window 2026-10-31 to 2026-11-13

| | |
|---|---|
| Paper profit at Round 22 size | **$+5,474.35** |
| Losing filled markets | 6 |
| Days with fills | 10 (green 90%) |
| Worst day | $-2,589.10 |
| Not in this test: index markets (Round 24) losing filled | 3 |

Filled or wrong markets are listed in [r21_fills.csv](r21_fills.csv) (837 rows).
