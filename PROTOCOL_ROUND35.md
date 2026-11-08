# Round 35 pre-registration: calls and puts on real option prices, $25,000 start, then scaled to $1,000

Written 2026-11-08, before the chains finish downloading.

## Data
Real end-of-day option chains (bid, ask, implied vol, delta) from DoltHub post-no-preference/options:
SPY, AAPL, MSFT, NVDA, AMZN, META, TSLA, GOOGL, daily from ~2020-03 to 2026-11 (about 6 expirations 2 weeks to
2 months out; strikes a few % apart). Underlying daily prices and ^VIX/^VIX3M from Yahoo; earnings dates from
DoltHub post-no-preference/earnings.

## Execution (identical for all)
Open and close at the **natural price**: sell at the bid, buy at the ask. $0.65 per contract per leg.
Expiry settles at intrinsic value from the underlying close. Equity marked at mid each day.
Risk: each position's maximum loss ≤ 5% of equity (3% for earnings trades); total open maximum loss ≤ 30%.
Entries checked on the first trading day of each week (earnings trades: the day before earnings).

## Strategies (17 configs)
- **S1 put credit spread (SPY):** sell the put nearest delta d ∈ {0.16, 0.30}, buy the next lower strike;
  expiry 25–50 days (nearest 35). Exit at 50% of the credit, or when the loss reaches 2× the credit, or at 21
  days left. Filters: none / trend (close > 200-day average) / IV rank > 30 / both. (8)
- **S2 iron condor (SPY):** 16-delta put spread + 16-delta call spread, same exits; filter none / IV rank > 30. (2)
- **S3 call credit spread (SPY)** at 30 delta when close < 200-day average. (1)
- **S4 call debit spread on breakouts (SPY):** close at a 55-day high and above the 200-day average; buy the
  ~50-delta call, sell the next higher strike; 45–70 days; exit +100%, −50%, close < 50-day average, or 14 days left. (1)
- **S5 put debit spread on breakdowns (SPY):** mirror of S4. (1)
- **S6 earnings (7 stocks):** at the close before earnings, (a) sell an iron butterfly (ATM straddle, wings at the
  nearest strikes ~8% away), (b) sell a 16-delta iron condor, (c) buy the ATM straddle; close at the close after
  earnings. (3)
- **S7 put credit spread only in VIX contango** (VIX < VIX3M), d = 0.30. (1)

## Split and pass
Dev 2020-03 → 2023-12 (choose); holdout 2024-01 → 2026-11 (judge). A config passes if on holdout: Sharpe ≥ 1.0,
worst drawdown better than −25%, annual return ≥ 15%, deflated Sharpe ≥ 0.95 for 17 trials, and dev return > 0.
**Combo:** the dev-best of each family that was profitable on dev, run together in one $25k account with the
risk budget split equally; judged the same way.

## Scaling to $1,000
Passing strategies are re-run at $1,000 with whole contracts. The data's strikes are a few % apart, so SPY spreads
here are ~$10–15 wide (max loss ~$1,000+ per contract): where that exceeds the risk limit at $1,000 the report says
so and gives the per-dollar return a $1–5-wide real spread would need.

Prediction written now: put spreads and condors make money most of the time but fail the Sharpe/drawdown bar
after natural fills (2020 and 2022); earnings iron flies are the best candidate; long debit spreads lose.

## Amendment before any real result (2026-11-08)

The backtester's synthetic check (Black-Scholes chains, options priced 60% above realized vol) showed the
pre-registered management (take 50%, stop at 2× credit, exit at 21 days) **losing** even when premium is rich:
it pays the bid/ask twice and cuts trades before the premium is earned; held to expiry the same spreads earn
(engine verified to the cent against a hand count). Added before any real data was run: **S1h**, the put credit
spread held to expiry, d ∈ {0.16, 0.30} × {no filter, trend} (4 configs). Total 21 configs; deflated Sharpe uses 21.
