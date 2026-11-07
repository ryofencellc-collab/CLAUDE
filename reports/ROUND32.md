# Round 32: the AP3X-style grid bot, tested independently

Rules: [PROTOCOL_ROUND32.md](../PROTOCOL_ROUND32.md). Binance 1-minute prices; fees 0.08%/side + $0.12/contract/side; broker liquidates when equity < margin × open notional.

## 1. Replicating the dashboard (XRP, from 2026-09-18 15:39, start price 1.3803)

| | dashboard | this replication (no margin calls) | with broker margin calls |
|---|---:|---:|---:|
| realized P&L (what the dashboard shows) | $1,898.79 | $-2,049.36 | $-358.29 |
| open positions now | 29 | 0 | 0 |
| unrealized P&L on them | not shown | $0.00 | $0.00 |
| **true equity (of $2,000)** | $3,898.79 shown | **$-49.36** | **$1,641.71** |
| lowest equity along the way | — | $-49.36 | $1,641.71 |
| liquidated by the broker | — | n/a | YES |

## 2. Every start date since 2023, held 50 days ($2,000 each)

| coin   | settings                                                               |   runs | realized > 0   | TRUE equity up   |   median true $ |   worst true $ | liquidated   |   median $/day (true) |
|:-------|:-----------------------------------------------------------------------|-------:|:---------------|:-----------------|----------------:|---------------:|:-------------|----------------------:|
| XRP    | dashboard (1% x 50, 20% margin)                                        |    452 | 34%            | 24%              |            -265 |          -1234 | 69%          |                 -5.31 |
| XRP    | tighter 0.5% x 50                                                      |    452 | 13%            | 11%              |            -247 |          -1108 | 92%          |                 -4.93 |
| XRP    | wider 2% x 50                                                          |    452 | 63%            | 47%              |             -30 |          -1466 | 42%          |                 -0.6  |
| XRP    | stop-loss 5 steps under the grid                                       |    452 | 34%            | 24%              |            -265 |          -1234 | 69%          |                 -5.31 |
| XRP    | no leverage (grid sized to $2,000; you own the coins, no margin calls) |    452 | 100%           | 27%              |             -36 |           -655 | 0%           |                 -0.71 |
| SOL    | dashboard (1% x 50, 20% margin)                                        |    452 | 15%            | 15%              |            -328 |           -838 | 100%         |                 -6.55 |
| SOL    | tighter 0.5% x 50                                                      |    452 | 4%             | 4%               |            -217 |           -625 | 100%         |                 -4.33 |
| SOL    | wider 2% x 50                                                          |    452 | 33%            | 31%              |            -502 |          -1043 | 75%          |                -10.03 |
| SOL    | stop-loss 5 steps under the grid                                       |    452 | 15%            | 15%              |            -328 |           -838 | 100%         |                 -6.55 |
| SOL    | no leverage (grid sized to $2,000; you own the coins, no margin calls) |    452 | 100%           | 38%              |             -23 |           -751 | 0%           |                 -0.46 |

## 2. Every start date since 2023, held 180 days ($2,000 each)

| coin   | settings                                                               |   runs | realized > 0   | TRUE equity up   |   median true $ |   worst true $ | liquidated   |   median $/day (true) |
|:-------|:-----------------------------------------------------------------------|-------:|:---------------|:-----------------|----------------:|---------------:|:-------------|----------------------:|
| XRP    | dashboard (1% x 50, 20% margin)                                        |    409 | 8%             | 8%               |            -380 |          -1234 | 97%          |                 -2.11 |
| XRP    | tighter 0.5% x 50                                                      |    409 | 6%             | 6%               |            -258 |          -1108 | 100%         |                 -1.44 |
| XRP    | wider 2% x 50                                                          |    409 | 46%            | 44%              |            -277 |          -1466 | 72%          |                 -1.54 |
| XRP    | stop-loss 5 steps under the grid                                       |    409 | 8%             | 8%               |            -380 |          -1234 | 97%          |                 -2.11 |
| XRP    | no leverage (grid sized to $2,000; you own the coins, no margin calls) |    409 | 100%           | 39%              |             -86 |           -830 | 0%           |                 -0.48 |
| SOL    | dashboard (1% x 50, 20% margin)                                        |    409 | 15%            | 15%              |            -326 |           -838 | 100%         |                 -1.81 |
| SOL    | tighter 0.5% x 50                                                      |    409 | 4%             | 4%               |            -215 |           -625 | 100%         |                 -1.19 |
| SOL    | wider 2% x 50                                                          |    409 | 18%            | 18%              |            -546 |          -1043 | 100%         |                 -3.03 |
| SOL    | stop-loss 5 steps under the grid                                       |    409 | 15%            | 15%              |            -326 |           -838 | 100%         |                 -1.81 |
| SOL    | no leverage (grid sized to $2,000; you own the coins, no margin calls) |    409 | 100%           | 48%              |              -7 |          -1259 | 0%           |                 -0.04 |

