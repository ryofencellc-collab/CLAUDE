# Fill realism check (0.1c price steps above 90c)

Kalshi now quotes 0.1c steps between 90c and $1 (price_level_structure 'tapered_deci_cent'). Our bid sits at
99c. A long-shot buyer who pays under 1c for the other side (e.g. 0.5c) trades with a bid ABOVE ours (99.5c),
not with us. The paper fill count treated every long-shot buy at <= 2c as flow that reached our level; any of
it that went to higher bids placed after ours was credited to us by mistake.

For every past paper fill this recounts, from Kalshi's public trade records, only the trades whose other-side
price is >= 1c (the only ones that can reach a 99c bid) and compares the resulting fills and P&L:

  old: filled = min(size, trades at other price <= 2c                  - queue at >= 99c when we bid)
  new: filled = min(size, trades at other price in [1c, 2c]           - queue at >= 99c when we bid)

'new' keeps the whole queue (including bids above 99c, which that flow never reaches): conservative.

Markets recounted: 433 (paper fills on Round 21/22 crypto markets). Generated 2026-11-07 16:13 UTC.

| | old count | new count | change |
|---|---:|---:|---:|
| long-shot contracts seen | 11,131,504 | 452,011 | -95.9% |
| paper P&L at 1k per market | $1,721.30 | $977.40 | -43.2% |
| markets filled at 1k | 433 | 359 | -74 |
| paper P&L at 10k per market | $7,239.18 | $1,085.36 | -85.0% |
| markets filled at 10k | 433 | 359 | -74 |

By series:

| series    |   pnl_old_1k |   pnl_new_1k |   pnl_old_10k |   pnl_new_10k |
|:----------|-------------:|-------------:|--------------:|--------------:|
| KXBTC15M  |       157.12 |         9.82 |       1562.43 |         98.26 |
| KXBTCD    |       549.65 |       549.65 |        549.65 |        549.65 |
| KXDOGE15M |       166.94 |        14.03 |       1072.24 |         16.38 |
| KXETH15M  |        29.46 |         0    |        294.78 |          0    |
| KXETHD    |       121.66 |       121.66 |        121.66 |        121.66 |
| KXSOL15M  |       146.12 |         8.28 |       1020.46 |          8.28 |
| KXSOLD    |       111.48 |       111.48 |        111.48 |        111.48 |
| KXXRP15M  |       286.22 |         9.82 |       2353.82 |         27    |
| KXXRPD    |       152.64 |       152.64 |        152.64 |        152.64 |

## If we bid higher than 99c (15-minute markets, 10k cap)

Flow a bid at each price would meet. 'no queue' assumes nobody ahead of us at that price (upper bound); 'full queue' subtracts everything that rested at >= 99c when we bid (lower bound). Profit per filled contract is 1 - price, minus the maker fee. Markets that lost would lose ~price per contract.

| bid | flow met | P&L, no queue | P&L, full queue |
|---|---:|---:|---:|
| 99.0c | 54,679 | $269.91 | $149.92 |
| 99.1c | 60,017 | $265.92 | $152.35 |
| 99.2c | 82,139 | $345.11 | $141.23 |
| 99.3c | 90,411 | $356.95 | $150.01 |
| 99.4c | 97,139 | $345.59 | $148.08 |
| 99.5c | 142,142 | $488.85 | $177.50 |
| 99.6c | 210,987 | $601.80 | $237.77 |
| 99.7c | 266,298 | $542.16 | $203.62 |
| 99.8c | 928,912 | $599.65 | $218.24 |
| 99.9c | 10,734,173 | $765.83 | $629.91 |

Losing markets in the recount: 0; filled under new count: 0.
