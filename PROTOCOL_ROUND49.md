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

## Amendment 1 (2026-11-13): data bug fixed before any valid result
The first run used Yahoo's Close, which is split-adjusted, while option strikes are not. Every split (AAPL 2020; NVDA
2021 and 2024; AMZN, GOOGL and TSLA 2022) looked like a 75–95% crash, and the output was nonsense (drawdowns of −26,760%).
Now the wheel runs on the spot implied by put-call parity from the chain itself (same basis as the strikes). A split is
detected on the day itself from the raw/adjusted ratio: shares are multiplied, the basis is divided, and any open
option is closed at its last pre-split mark. Buy-and-hold uses split-adjusted prices. On synthetic data with a planted
4:1 split, the wheel gives the same result with and without the split. The rules are unchanged.

## Result (2026-11-13): **0 of 3 pass** (`reports/ROUND49.md`)
Holdout 2024–26, equal-weight across 8 names: the wheel made +12.7% (W1, 30-delta), +11.6% (W2, 16-delta) and +19.3%
(W3, calls never below cost), with Sharpe 0.74–1.08, against buy-and-hold's +29.7% and Sharpe 1.24. Drawdowns were a
little smaller (−18% to −24% vs −28%), but the wheel caps the upside on exactly the stocks that ran (NVDA +7–11% vs
+62%). Known glitch: the dev rows for AMZN and GOOGL in W1/W2 are still wrong around their 20:1 splits (2022). It
does not touch the holdout, and it does not change the verdict.
