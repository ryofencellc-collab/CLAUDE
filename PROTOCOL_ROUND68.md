# Round 68 pre-registration: catalyst dissection of 0DTE straddle hits and flops

Written 2026-11-20, before any Round 68 data is joined or any result is seen.

## Question (the user's)
"Clearly there's a catalyst." For every day the 0DTE straddle sale is placed (Round 67's A trade, 2022-06 → 2026-11):
1. Which catalyst drove the move?
2. When in the day did the damage happen?
3. Could the catalyst have been known before the trade? If so, was the option price already charging for it?

## Data
- **Release calendar from Kalshi markets** (exact release minute = market close + 1 min):
  - CPI (KXCPI), jobs (KXPAYROLLS / KXU3), GDP (KXGDP), PPI (KXUSPPI), retail sales (KXUSRETAIL), PCE (KXPCEHEAD), jobless claims (KXJOBLESSCLAIMS, plus every Thursday by rule).
  - Fed decisions: KXFEDDECISION / KXFED, plus federalreserve.gov FOMC dates.
  - Coverage start is reported per type, and each type is evaluated only within its coverage.
- **Mega-cap earnings** (NVDA, AAPL, MSFT, AMZN, GOOGL, META, TSLA, AVGO) from yfinance. A report after 16:00 tags the next trading day; one before 09:30 tags that day.
- **Minute S&P:**
  - HistData SPXUSD for intraday timing and the 08:30 pre-open reaction (it trades pre-market), through 2026-10-30.
  - After that, Yahoo ^GSPC 1-minute bars for the session and ES=F for pre-market.
- **Daily data:** VIX1D, VIX and SPX as in Round 67. Dev < 2024-08-12 ≤ holdout.

## Descriptive dissection (reported whatever happens)
- **T1, by catalyst type:**
  - days, and how rich options were priced (VIX1D/VIX);
  - realized/implied move (|C−O|/σ), mean straddle P&L, flop rate, worst day;
  - share of all straddle losses.
- **T2, where the damage happened:** split each day's |C−O| into signed half-hour contributions (they sum to |C−O|).
  - Report the average profile on all days, flop days and the 50 worst days.
  - Report the share of the 50 worst days whose largest damage half-hour contains a scheduled release time (10:00, 14:00, 14:30).
- **T3, the 50 worst days:**
  - catalyst tags, earnings tags, the 08:30 pre-open reaction (|ΔS 08:29→08:45|/σ) and the damage window;
  - plus the largest single 5-minute move and its time.
- **T4, scheduled vs unscheduled:** share of total losses on days with any scheduled tier-1 or tier-2 release or mega-cap earnings, versus days with none.

## Pre-registered ex-ante rules (sell the straddle at the open, as A, except on skipped days)
- **E1:** skip tier-1 days (CPI, jobs, FOMC decision).
- **E2:** skip tier-1 and tier-2 days (PPI, retail sales, GDP, PCE).
- **E3:** skip the day after (or the day of a pre-market) NVDA/AAPL/MSFT/AMZN/GOOGL/META earnings.
- **E4:** skip if the 08:30 → 09:29 pre-open move is ≥ 0.5σ (σ = the day's VIX1D 1-day move).
- **E5:** E1 ∪ E3 ∪ E4.

Pass for any E rule, on the holdout:
- mean > 0 and t ≥ 2.5;
- mean above the unfiltered holdout mean;
- max drawdown ≤ the unfiltered max drawdown;
- both holdout halves positive;
- five rules tested, and t ≥ 2.5 already exceeds a Bonferroni-5 one-sided 1%.

A pass goes to the real-quote forward test, not to money.

## Late entry (descriptive only, model-priced)
Sell at 10:05, 11:30, 13:00 or 14:35 instead of the open. Premium for the rest of the day:
- S_T · VIX1D_open/100 · sqrt(f_T/252) · sqrt(2/π) · A(T)/A(open), using the Round 66 calibrated time-of-day curve;
- times the Round 66 M1 adjustment (rv30_T / VIX1D_open)^0.457;
- P&L = premium − |C − S_T| − 0.6.

The model is not trusted for levels, so this is never a pass. It shows how much of the flop damage a later entry would have avoided, and what it gives up.

## Verdict (2026-11-20): FAIL (no pre-registered skip rule passes). Findings:
- **Unscheduled news, not the calendar, drives the losses.**
  - Days with no scheduled release or mega-cap earnings carry 73% of all straddle losses and 29 of the worst 50 days. Their options are priced cheapest (VIX1D/VIX 0.67).
  - In only 7 of the worst 50 days did the biggest damage start at a scheduled time (10:00, 14:00, 14:30). The damage builds over 10:30–11:30 and again 15:00–16:00, i.e. trend days.
- **Scheduled macro is priced in.**
  - Options charge more on FOMC (VIX1D/VIX 0.88), jobs (0.75) and CPI (0.73) days.
  - CPI days earned +5.1 pt and FOMC days −0.2. Skipping CPI/jobs/FOMC (E1) lowered the holdout mean, 1.65 vs 2.04.
- **Mega-cap earnings mornings are the one known-in-advance loser:** mean −3.7 pt on 49 days (NVDA −7.7 on 18), 9 of the worst 50.
  - Skipping them (E3) gave holdout +2.18, t 1.5: better than base but far below 2.5.
- **Thursdays are weak in both periods** (dev +0.85, holdout −1.76, vs +3–8 on other days).
  - Skip-Thursday on the holdout: +2.97, t 2.03.
  - Not pre-registered here (weekday filters were in Round 67's search and did not rank), so it is a lead only.
- **Late entry after a quiet morning** (model-priced, descriptive) loses money at 11:30 and 13:00. The afternoon premium is too small for the afternoon move plus costs.
