# Round 4 results: "beat the retail trader"

Rules: [PROTOCOL_ROUND4.md](../PROTOCOL_ROUND4.md). Runs
[40100952367](https://github.com/ryofencellc-collab/CLAUDE/actions/runs/40100952367) (crowd)
and [40101597790](https://github.com/ryofencellc-collab/CLAUDE/actions/runs/40101597790)
(sweep, after the timestamp-resolution fix; the first sweep run was broken
by the same bug as Round 2 section A). Cumulative trials: 171.

**Verdict: 0 of 3 families passed.**

## A. Crypto: trade against retail positioning (BTC, ETH, SOL, XRP, DOGE; holdout 2024-01 on)

| Strategy | IS Sharpe | IS return | Holdout Sharpe | Holdout return | Holdout trades | Win rate | Green days |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fade retail, z>1.5, hold 4h | −2.19 | −56% | −4.18 | −92% | 6,049 | 42% | 28% |
| Fade retail, z>1.5, hold 24h | +0.59 | +16% | −0.07 | −14% | 1,765 | 46% | 43% |
| Fade retail, z>2.0, hold 4h | −0.63 | −21% | −2.25 | −57% | 2,366 | 43% | 31% |
| **Fade retail, z>2.0, hold 24h** *(selected)* | **+0.78** | **+24%** | **−0.14** | **−11%** | 809 | 47% | 44% |
| Follow whales vs retail, hold 4h | −0.77 | −2% | +0.39 | +2% | 62 | 50% | 47% |
| Follow whales vs retail, hold 24h | −0.77 | −2% | +0.97 | +11% | 24 | 58% | 54% |

Fading the crowd worked in 2022–23 (a bear market, where retail kept buying
dips) and stopped working in 2024–26. The 4-hour versions show what frequent
trading does: fees alone lost 57–92%. "Follow the whales" fired only 24–62
times in nearly 5 years, too rare to judge or to live on.

## B. Nasdaq-100: fade the prior-day liquidity sweep (stop hunts)

| Window | Target | IS trades | IS win rate | IS Sharpe | Holdout trades | Holdout win rate | Holdout total | Holdout Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 09:30–11:00 | 1.5R | 1,335 | 43% | −1.76 | 437 | 43% | −48R | −1.09 |
| 09:30–11:00 | 3R | 1,323 | 35% | −1.33 | 436 | 37% | −19R | −0.32 |
| 09:30–16:00 | 1.5R | 2,188 | 42% | −2.37 | 692 | 42% | −82R | −1.33 |
| 09:30–16:00 | 3R | 2,141 | 31% | −1.88 | 680 | 33% | −48R | −0.59 |

Null test: 0 passes. A sweep of yesterday's high and snap-back is not a
reliable reversal signal: price keeps going about as often as it reverses,
and costs make it a loser.

## What this says about "beating retail"

Retail positioning and retail stop levels are visible in the data, but
trading against them did not pay after costs, out of sample. The players who
profit from retail flow (market makers, payment-for-order-flow (PFOF) buyers,
exchanges) earn the spread and fees on the other side of every trade, not a
directional bet. That's a business with infrastructure and licences,
not a strategy a $1,000 account can copy.
