# Round 5 results: Kalshi weather markets

Rules: [PROTOCOL_ROUND5.md](../PROTOCOL_ROUND5.md) (with amendments 1–2). Run
[40116008981](https://github.com/ryofencellc-collab/CLAUDE/actions/runs/40116008981)
(parallel per-city fetch). 61,072 settled contracts, 17 cities with usable
data (14 major US, 3 minor), 2021-08 → 2026-10. Cumulative trials: 195.

**Verdict: 0 of 4 combinations passed.**

## What happened

- **Prices only exist for recent markets.** Kalshi's archive returns the
  contracts back to 2021 but no hourly bid/ask history before mid-2026. So
  the in-sample period has forecasts and settled temperatures (used to
  calibrate each city's forecast bias and spread) but no tradable prices. The
  pre-registered selection rule (best in-sample ROI) therefore can't pick a
  config. All 24 configs are shown on the 120-day holdout instead. Every one
  of them is a genuine out-of-sample test, since calibration used only
  pre-holdout data.
- **The model lost in the big cities, every way it was run:**

| Forecast | Cities | Best version (holdout) | Worst version |
|---|---|---|---|
| GFS (one model) | 14 major | −16.7% ROI, 941 bets, −$1,572 | −35.8%, 3,890 bets, −$13,908 |
| 5-model average | 14 major | −19.0% ROI, 943 bets, −$1,791 | −37.4%, 3,627 bets, −$13,574 |
| GFS | 3 minor | +72% on 59 bets (p = 0.25, noise) | −14.1% on 249 bets |
| 5-model average | 3 minor | +12% on 109 bets (p = 0.43) | −32.0% on 275 bets |

Win rates 25–39%, green days 10–38%. The few positive cells are tiny samples
that come nowhere near significance (p × 195 ≫ 0.05), and the same idea with
better forecasts (5 models) did *worse* in those cities, which is what
noise looks like.

## Why the market wins

At 09:00 on the day, the market already knows the overnight model runs, the
morning temperature readings, and what bots running the same models are
doing. To rule out look-ahead, our backtest could only use forecasts made
about a day earlier. **A day-old forecast loses to a market that has today's
information.** Kalshi weather is not retail traders guessing: it's priced
by people with fresher data than a fair backtest can use.

The "bet every bracket" versions lost 28–37%: a normal-curve model
overprices the cheap tail brackets (5–15¢ contracts that almost never hit).

## What would be a fair next test

Only a **live forward test** can use same-morning data without look-ahead:
at 09:00 local, pull the latest model runs and live Kalshi quotes, and log
paper bets in git before the outcome is known (as with football). This
backtest gives no reason to expect it to work, so it's optional.
