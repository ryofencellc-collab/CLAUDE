# Round 51 pre-registration: model-priced backtest of the 0DTE opening-range breakout (B1)

Written 2026-11-17, before running.

**Why.** Real historical intraday option quotes are paid data. An at-the-money option is well approximated by
Black-Scholes with the market's own 1-day implied volatility (VIX1D). So B1, which buys the ATM 0DTE call or put, can be
replayed on free 5-minute SPY bars (Yahoo, the last 60 days).
**Rule (same as Round 39 B1).** Opening range = the 09:30–10:00 ET bars. After 10:00, the first 5-minute close above
the range high (below the low) buys the ATM call (put) at that close. Price = Black-Scholes, σ = that day's VIX1D
open / 100, time to the 16:00 expiry, rate 4%. Exit at the first 5-minute close where the value is ≥ 2× (target) or
≤ 0.5× (stop) the entry, else at 15:45. One trade a day. Costs: 3% of the option price on entry and on exit
(spread/slippage) plus $0.65 per side.
**Calibration check.** On days that overlap the real-quote forward test (Round 39b, 2026-11-09 →), compare the model's
trade direction, exit type and ROI with the real ones. The model counts as usable only if direction agrees on ≥ 90% of
days and exit type on ≥ 75%.
**Reported.** Trades, win rate, mean ROI per trade, total, worst trade, and the same for a "no-signal" baseline
(buy the ATM call at 10:00 every day).
**Pass (screen only, since it is model-priced):** mean ROI per trade > +10% with t ≥ 2 over ≥ 30 trades, and the
calibration check passes. A pass does not fund anything. It raises priority on getting real historical quotes.
