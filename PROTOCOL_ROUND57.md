# Round 57: gas-price nowcast vs Kalshi's daily AAA gas markets (written 2026-11-18, before any results)

**Idea (autonomous backlog #57):** Kalshi's KXAAAGASD* markets ask "will AAA's average regular gas price for <US / state> on day D be above $K?".
Each market opens at 08:00 ET on D−1 and closes at 23:59 ET on D−1, before AAA publishes D's number. The D−1 number is public
all day on D−1. Retail gas prices are sticky and trend for days ("rockets and feathers"). If traders don't use the trend, a simple
nowcast should beat the price.

**Data.**
- **Markets:** every settled market in the KXAAAGASD* series (national and states) from 2026-09 → now. The settlement value (`expiration_value`)
  of each day's event gives the AAA value history.
- **Prices:** the market's own trades. A YES buy uses trades whose taker bought YES (the ask); a NO buy uses trades whose taker bought NO.

**Model** (frozen; three variants). V = yesterday's settled value, Δ = daily changes.
- `persist`: μ = 0.
- `mom3`: μ = mean Δ over the last 3 days.
- `mom7`: μ = mean Δ over the last 7 days.

In all three, σ = std of Δ over the last 10 days (minimum 5 observations, floor $0.002), and p(YES) = 1 − Φ((K − V − μ)/σ).

**Trade.** For each market, take the first ask-side trade after 12:00 ET on D−1 for each side.
- Buy YES if p − ask ≥ e; buy NO if (1 − p) − no_ask ≥ e.
- 1 contract, taker fee 0.07·x·(1−x) rounded up to the cent, settlement at $1/$0.

**Dev/holdout.** Dev covers closes before 2026-10-20; holdout covers 2026-10-20 → now.
- On dev, pick (variant, e) from 3 × {0.05, 0.10, 0.15, 0.20} = 12 configurations by mean P&L, requiring ≥ 30 trades.
- **Pass (holdout):** all of
  1. mean P&L > 0 per contract;
  2. day-clustered t ≥ 2.5;
  3. ≥ 100 trades;
  4. the model's Brier score beats the market price's Brier score on the same holdout markets.

Capacity (contracts available at those prices) is reported but is not part of the pass.

**Calibration:**
- **Planted:** a synthetic world where gas trends and prices ignore the trend → must pass.
- **Null:** a synthetic world where prices equal the true probability plus noise → must not pass.

## Result (2026-11-18): **FAIL** (`reports/ROUND57.md`)
- **Sample:** 46,883 settled markets in 51 series (US + states), 2026-09-11 → 11-17.
- **Dev choice:** mom7 with edge 0.20. No dev configuration reached t ≥ 1.
- **Holdout:** 2,014 trades, −$0.016 per contract, t −0.94.
- **Brier:** the market price scores **0.047** against the model's 0.143. The market is about 3× more accurate than the nowcast.
- **Reading:** gas traders evidently use better live data (station-level feeds such as GasBuddy) than yesterday's AAA print plus a trend.
  Public-statistic markets that are this liquid look efficient. The nowcast category stays open only for thin markets with no live alternative data.
