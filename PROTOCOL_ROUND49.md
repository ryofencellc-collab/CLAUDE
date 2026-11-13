# Round 49 pre-registration: the options "wheel" (Reddit r/options / r/thetagang staple)

Written 2026-11-13, before running. Data: Round 35's real end-of-day option chains (DoltHub), SPY and AAPL, MSFT, NVDA,
AMZN, META, TSLA, GOOGL, 2020-03 → 2026. Dev 2020-03 → 2023, holdout 2024 → 2026. Fills at the natural price (sell at the
bid), $0.65 per contract, daily marks at mid. Dividends ignored for both the wheel and buy-and-hold.

**Wheel (1 contract per symbol, cash-secured).** Start with cash = 100 × spot. With no shares, sell 1 put, 25–45 days
to expiry (closest to 30), at delta closest to D. At expiry, below the strike: assigned 100 shares at the strike; else keep
the premium and sell the next put the next day. With shares, sell 1 call at delta D, 25–45 days. Above the strike at
expiry: called away; else keep the shares and sell another call.
- W1: D = 0.30. W2: D = 0.16. W3: D = 0.30, with calls only at strikes ≥ the assignment price (never lock in a loss).
**Benchmark.** Buy and hold 100 shares from the same start.
**Pass (holdout).** The equal-weight wheel across the 8 symbols has Sharpe ≥ 1 and CAGR ≥ 15%, and a higher Sharpe than
equal-weight buy-and-hold. It also has to beat buy-and-hold's Sharpe on dev.
