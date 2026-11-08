# Round 36 pre-registration: beating retail traders' documented mistakes (US stocks)

Written 2026-11-08, before any data is fetched.

## Why
Retail traders chase attention spikes and lottery-like stocks (Barber, Huang, Odean & Schwarz 2022, "Attention-
induced trading and returns: evidence from Robinhood users": heavily herded-into stocks fall ~5% over the next
month; Bali, Cakici & Whitelaw 2011 "MAX effect"; George & Hwang 2004 "52-week high"; short-term reversal; the
turn-of-the-month effect). An AI can scan thousands of stocks every day without emotion.

## Data
Universe: every common stock in the NASDAQ Trader symbol directory (Nasdaq + NYSE/other listings; no ETFs, test
issues, warrants, units, preferreds). Daily OHLCV from Yahoo, 2015-01 → 2026-11. Tradable on a day only if price ≥
$3 and 20-day average dollar volume ≥ $5M (penny-stock test excepted). **Survivorship bias:** delisted stocks are
missing; this flatters long-side tests and understates short-side ones; reported, not corrected.

## Execution
Signal known at a day's close; enter at the next day's open; exit at the close of the holding day. Costs 0.10% per
side (0.20% round trip) plus, for shorts, 10%/yr borrow (frenzy stocks are expensive to borrow). Event strategies run
10 slots (each 10% of capital, unused cash earns 0); cross-sectional strategies are equal-weighted deciles, costs
charged on turnover.

## Tests (26 configs)
1. **Frenzy fade:** 1-day return ≥ +20% and volume ≥ 5× its 50-day average → short, hold H ∈ {1, 5, 20} days.
2. **Panic bounce:** 1-day return ≤ −20%, volume ≥ 5× → long, H ∈ {1, 5, 20}.
3. **Frenzy chase:** same trigger as 1 → long, H ∈ {1, 5}.
4. **MAX / lottery effect:** monthly, short the top decile by largest single-day return last month, long the bottom
   decile (long-short), and the short leg alone.
5. **52-week high:** monthly, long the decile closest to its 52-week high, short the farthest (long-short).
6. **Gap-up fade:** open ≥ +10% above the prior close on volume ≥ 3× → short at the open, cover at that day's close
   (thresholds 10% and 20%).
7. **Gap continuation (earnings-style):** close-to-close ≥ +5% with volume ≥ 3× → long H ∈ {5, 20}; ≤ −5% → short
   H ∈ {5, 20}.
8. **Weekly reversal:** weekly, long the bottom decile of 5-day return, short the top decile (long-short).
9. **Penny stocks:** monthly, short stocks under $5 (with ≥ $1M dollar volume) vs long the market-cap-proxy rest.
10. **Turn of the month:** long SPY from the last trading day of the month to the 3rd trading day.

## Split and pass
Dev 2015-01 → 2021-12, holdout 2022-01 → 2026-11. A config passes if: dev return > 0, holdout annual return > 0,
holdout Sharpe ≥ 1.0, and holdout t-stat of mean daily return ≥ 3.0 (strict, for 26 tries).

Prediction written now: frenzy fade and the MAX short leg are the best candidates; panic bounce and gap
continuation are coin flips after costs; turn-of-month is small but real.

## First run (2026-11-08) rejected as a data artefact; strict rerun

The first run "passed" frenzy fades at +100% to +430%/yr with −60% to −95% drawdowns, while every long strategy lost
85–96%/yr. That pattern is the signature of two known traps, not of an edge: (1) Yahoo's adjusted prices inflate the
past prices of stocks that later reverse-split, so the "$3" filter admitted real penny stocks (mostly unshortable);
(2) the universe is today's listings, heavy with small caps that collapsed but survived. **Rerun (pre-registered here,
same tests and pass rule):** price filter on the real unadjusted close ≥ $10, 20-day dollar volume (real price) ≥ $50M,
returns from split/dividend-adjusted prices, costs 0.15% per side, hot-short borrow 20%/yr. The first run's table is
kept in git history only.

## Second rerun (2026-11-08): the "raw" close was still split-adjusted

The strict rerun still showed frenzy-fade shorts at +256%/yr and long gap-ups at −75%/yr among "≥ $10, $50M/day"
stocks, which is implausible for liquid stocks. Cause: Yahoo's unadjusted `Close` is already split-adjusted, so a stock
that later did a 1-for-50 reverse split still showed a fake $10 history. Fix: download split history and rebuild the
price that actually traded (multiply by every later split ratio); filters use that. Added a sanity line: the
equal-weighted average tradable stock's return; if it is far from ~10%/yr the table is not to be trusted.
