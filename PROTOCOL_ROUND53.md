# Round 53 pre-registration: exhaustive New York-session grid on S&P and Nasdaq micro futures

Written 2026-11-17, before running. The user asked for "every strategy and combination" for the NY session.

**Data.** HistData 1-minute S&P 500 (SPXUSD) and Nasdaq-100 (NSXUSD) bars, New York time, 2012 → now. The regular session
09:30–15:59 (390 bars; days with < 380 bars are skipped). Also used: prior session close/high/low, the overnight range
(18:00 → 09:29), a 20-day average of closes, and the prior day's range. Dev 2012–2020, holdout 2021 → now.
**Fills.** A signal on bar k's close fills at bar k+1's open. If stop and target fall in one bar, the stop counts. A gap
through the stop fills at the open. The trade is flat at the exit time's close. Round-trip slippage: 0.5 pt (S&P) / 1.25
pt (Nasdaq); $1.24 commission per micro; MES $5/pt, MNQ $2/pt; size so the stop risks ≤ $250 (1–15 contracts). One
trade per day per configuration.

**Entry families (16).**
- ORB n ∈ {5, 15, 30, 60} min: first close beyond the opening range.
- OR-fade n ∈ {15, 30}: after a close beyond the range, the first close back inside → trade the other way.
- Gap-fill g ∈ {0.2%, 0.5%}: at 09:31, fade the gap; target the prior close (overrides R).
- Gap-and-go g ∈ {0.2%, 0.5%}: at 09:45, if price is still beyond the open in the gap's direction, trade with the gap.
- First-hour trend th ∈ {0.2%, 0.4%}: at 10:30, trade with the 09:30→10:30 move if beyond ±th.
- Prior-day high/low breakout (first close beyond, after 09:35).
- Overnight high/low breakout (first close beyond, after 09:35).
- Power hour: at 15:00, trade with the day's move if beyond ±0.3%; flat 15:59.
- Stretch fade: first close ≥ 0.5% from the 30-bar average after 10:00 → fade toward it.
**Stops (3).** Structure (range side for ORB/fade/level breakouts, else skipped), 0.25%, 0.5% of entry.
**Targets (4).** 1R, 2R, 3R, none (time exit).
**Exit time (2).** 11:30, 15:55 (power hour always 15:59).
**Filters (6).** None; with the gap (side = gap direction); with the 20-day trend (prior close vs its 20-day average);
skip Mondays and Fridays; high volatility (prior day range ≥ its 60-day median); low volatility.
Every combination runs on both markets: about 4,600 configurations.

**Pass (all required, holdout).** Mean R > 0 with t ≥ 3; dev mean R > 0 with t ≥ 2; deflated Sharpe ≥ 0.95 on holdout
daily P&L, with the number of trials = every configuration run; the same configuration has mean R > 0 on the *other*
market's holdout; prop-firm pass rate ≥ 50% and expected value per attempt > 0 (Round 52 rules). Everything is reported,
top 40 by holdout t. A pass goes to forward paper trading. Nothing is funded on this alone.
