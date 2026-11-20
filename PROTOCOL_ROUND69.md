# Round 69 pre-registration: blind test of the frozen 0DTE strategy

Written 2026-11-20 evening, before any Round 69 number is computed.

## The strategy (frozen; nothing may change after this)
- Sell the SPX 0DTE ATM straddle at the open and hold it to the cash-settled close.
- **Skip Thursdays.**
- **Skip mornings after NVDA/AAPL/MSFT/AMZN/GOOGL/META earnings** (reported after the prior close, or before this open).
- **Both filters could have been found on dev alone** (2022-06 → 2024-08-11):
  - Thursday was the worst weekday there (+0.85 pt vs +1.8 to +8.3 on other days).
  - Earnings mornings averaged −4.5 pt vs +4.4 on other days.
  - So scoring from 2024-08-12 on is a fair blind test of a rule chosen on dev.

## Test 1: real recorded quotes (the real test; tiny sample)
- **Days:** every recorded SPXW day: Cboe 1-minute data 2026-11-09 → 11-19, plus the Yahoo 5-minute data for 11-20.
  - The 11-20 recording starts at 10:32 ET, so that day's entry is the first snapshot. This is reported separately.
- **Entry:** the first snapshot at or after 09:31 ET. Sell the call and put at the strike nearest spot, **at the bid**.
- **Settlement:** official SPX close. Fees $1.50 per contract per leg.
- **P&L ($ per straddle):** (bid_call + bid_put − |close − K|) × 100 − 3.00.
- **The curve:**
  - the same trade on every recorded day, including Thursdays and earnings mornings;
  - buy-and-hold S&P over the same days.

## Test 2: the blind holdout (model-priced, 2024-08-12 → 2026-11-19)
- Day P&L from Round 68 (`data/r68_days.csv`).
- Reported three ways:
  - as modelled;
  - with the real-quote haircut: premium × 0.895, the median real/model ratio measured on recorded days in Round 67;
  - with the haircut and the real median spread (0.50 pt half-spread already in the 0.6 cost).
- **Compared with:** every day, and SPX buy-and-hold.
- **Pass:**
  - on the holdout with the haircut, the strategy's mean is > 0 with t ≥ 2;
  - it beats the every-day trade on mean P&L and on max drawdown;
  - Test 1 does not contradict it (real-quote mean ≥ 0 on traded days).
