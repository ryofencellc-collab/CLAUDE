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

## Result (2026-11-08, reports/ROUND35.md): 0 of 21 pass; one real but small edge

Holdout benchmark, SPY buy-and-hold: 16.8%/yr, Sharpe 1.07, worst drop −19%.

- **Best and most consistent: S1h, 16-delta SPY put credit spread, only above the 200-day average, held to expiry.**
  Dev 4.8%/yr (Sharpe 1.67); holdout **6.9%/yr, Sharpe 1.51, worst drop −6%, 93% of trades won** ($25k → $30,257).
  It fails only the 15%/yr bar (and deflated Sharpe over 21 trials). Good risk-adjusted, too small at this risk level.
- The trend filter helps every put-spread variant; holding to expiry beats the 50%/2×/21-day management in 3 of 4.
- Iron condors, call spreads in downtrends, put debit spreads on breakdowns: lose in both periods.
- Call debit spreads on breakouts: lose on dev, +4.7%/yr on holdout (Sharpe 0.55): not reliable.
- Earnings (iron fly, condor): roughly flat. Data limit: the chains carry only expirations ≥ ~2 weeks out, so these
  trades could not use the weekly options where the post-earnings IV crush is concentrated. Long straddles could
  not be sized at 3% risk on these stocks (no trades).
- The combo (dev-best of each family) made 17%/yr on dev but 4.2%/yr on holdout: the dev winners did not hold up.

Losses cluster in sharp selloffs (Jul 2024, Feb–Apr 2025, Feb–Apr 2026): the worst single spreads lose ~$1,000 (4%).
