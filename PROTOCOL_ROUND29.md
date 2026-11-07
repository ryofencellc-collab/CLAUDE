# Round 29 pre-registration: three documented stock/crypto effects, tested for daily income

Written 2026-11-07, before any data it will be judged on is loaded.

## Why these three

Research (Nov 7): crypto funding/basis carry has compressed to ~0–8%/yr in 2026 (BIS WP 1087; 2026
write-ups), so it is not tested. The three that remain and can compound daily:

1. **Crypto big-move reversal.** Intraday Bitcoin returns show negative autocorrelation at 1–4 h, stronger after
   larger moves (Univ. Munich working paper). Test: at each hour, if the past H-hour return is beyond k standard
   deviations (σ of H-hour returns over the past 30 days), take the opposite side for H hours.
   Grid H ∈ {1, 2, 4} × k ∈ {2, 3, 4} (9 configs). BTC, ETH, SOL, XRP, DOGE (Binance 1-minute), capital split
   equally, one position per coin. Cost 0.14% round trip (perp taker 0.05% ×2 + 0.02% slippage ×2).
2. **Intraday momentum** (Gao, Han, Li & Zhou, JFE 2018). The return from the prior 16:00 close to 10:00 ET
   predicts 15:30–16:00. Test on Nasdaq-100 1-minute bars (HistData, 2012+): trade 15:30→16:00 in the sign of
   that return, only on days where its size is above the q-quantile of the past 250 days, q ∈ {0, 0.5, 0.8}.
   Cost 1.25 index points round trip.
3. **Overnight drift** (Cliff, Cooper & Gulen). Hold SPY / QQQ / IWM from the close to the next open
   (dividend-adjusted, Yahoo). Variants: every night; only after an up day; only after a down day (3 × 3 = 9).
   Cost 2 bp round trip.

## Split

| | crypto reversal | intraday momentum | overnight |
|---|---|---|---|
| dev (choose the config) | 2024-01 → 2025-12 | 2012 → 2019 | 2000 → 2015 |
| holdout (judge it) | 2026-01 → 2026-10 | 2020 → 2026 | 2016 → 2026 |

The config with the best dev Sharpe (after costs) in each family is the only one judged on holdout.

## Pass (holdout, after costs)

Net return > 0; Sharpe ≥ 1.0; worst drawdown better than −30%; deflated Sharpe ≥ 0.95 for the family's trial count.

## What is reported for the user

For each family: what $1,000 earned per day on holdout at 1× exposure, and the leverage that would be needed
for $100/day with the drawdown that leverage implies.

Prediction written now: crypto reversal is the only one with a chance; intraday momentum has likely decayed
since publication; overnight drift is real but too small after costs to matter at $1,000.

## Result (2026-11-07, reports/ROUND29.md): 0/3 pass

- Crypto reversal: every one of the 9 configs lost money on dev (2024–25); the least-bad one made 10.6% on 2026
  (Sharpe 1.4) but fails the deflated-Sharpe check: a 1-in-9 pick that lost in the earlier period. $0.34/day on $1,000.
- Intraday momentum: lost on dev, small gain since 2020 (Sharpe 0.55). $0.10/day on $1,000.
- Overnight drift: real but small (Sharpe 0.59, −20% drops). $0.24/day on $1,000.

None comes near $100/day on $1,000; the leverage needed (290–990×) turns their normal dips into a wipe-out.
The prediction was right except that crypto reversal did not survive either.
