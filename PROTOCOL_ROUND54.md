# Round 54: the NY-session system on 7 markets, plus the segment scanner (written 2026-11-18, before any data)

**Why:** Round 53 tested only the S&P and Nasdaq; the blind test showed the grid misses weekday, midday and short gap effects.
This round widens both: more markets, and both detectors on each.

**Markets** (HistData 1-minute, 2012 → now, NY time; costs per round trip in basis points of price):

| Market | Cost (bp) |
|---|---|
| S&P (SPXUSD) | 1 |
| Nasdaq (NSXUSD) | 1.5 |
| Gold (XAUUSD) | 2 |
| WTI oil (WTIUSD) | 3 |
| EURUSD | 1 |
| USDJPY | 1 |
| GBPUSD | 1.5 |

**Detector 1:** the Round 53 grid, unchanged, 1,728 configurations per market. It is scored in R after costs.
- **Screen:** holdout (2021+) t ≥ 3 and dev (2012–2020) t ≥ 2, both positive.
- **Pass:** also deflated Sharpe ≥ 0.95 with N = all configurations in the round.

**Detector 2:** the segment scanner from `run_blind.py`, unchanged, on all 7 markets at once (Bonferroni over every test).
- **Pass:** same sign in both periods, and the mean beats the market's cost + 1 bp.

**Calibration** (done before this round, `reports/blind_calibration.md`): the grid finds ORB, power-hour and overnight-momentum edges
of k ≥ 0.25–0.35 within 2 years; the scanner also finds midday and weekday edges. Over 14 years the detection floor is roughly half that.

Anything that passes is a hypothesis for live paper trading, not money.

## Result (2026-11-18): **0 pass on either detector** (`reports/ROUND54.md`)
- **Grid:** 12,096 configurations, 0 screen candidates. The share of configurations that made money in 2021+ after costs:

  | Market | Share profitable |
  |---|---|
  | S&P | 33% |
  | Nasdaq | 37% |
  | Oil | 19% |
  | USDJPY | 14% |
  | Gold | 10% |
  | GBPUSD | 9% |
  | EURUSD | 8% |

  The best was the USDJPY prior-day breakout on low-volatility days, with t about 2.5 in both periods. That is well short of the 4.3 that 12,096 trials need.
- **Scanner:** 1,869 tests, 0 significant.
