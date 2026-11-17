# Round 52 pre-registration: New York and Asia session strategies on S&P/Nasdaq micro futures, scored as a prop-firm account

Written 2026-11-17, before running. Prompted by a TikTok prop-firm trader who trades the New York and Asia sessions
on MES (Micro E-mini S&P). His exact rules are unknown, so the standard setups for those sessions are tested.

**Data.** HistData 1-minute S&P 500 (SPXUSD) and Nasdaq-100 (NSXUSD) index CFD bars, 24 hours, 2012 → now, in
New York time (a proxy for ES/NQ futures). Dev 2012–2020, holdout 2021 → now. Fills: signal on a bar's close, filled at
the next bar's open; if stop and target fall in one bar, the stop counts; a gap through the stop fills at the open;
round-trip slippage 0.5 point (S&P) / 1.25 points (Nasdaq) plus $1.24 commission per micro contract.
**Contracts.** MES = $5/point, MNQ = $2/point. Size so the stop risks ≤ $250 on a $50k account (at least 1 contract,
at most 15).

**Setups (one trade per session per day).**
- NY1 opening-range breakout 15 min: range 09:30–09:45; first 1-minute close outside it; stop at the other side; target 2R; flat 11:30.
- NY2 opening-range breakout 30 min: range 09:30–10:00; target 1R; flat 12:00.
- NY3 first-hour trend: at 10:30, if the 09:30→10:30 move is beyond ±0.3%, trade with it; stop 0.4%, target 0.8%; flat 15:55.
- AS1 Asia range → London breakout: range 19:00–02:00; first close outside it 02:00–05:00; stop at the range middle; target 1R; flat 08:00.
- AS2 Asia mean reversion: 20:00–01:00, when price is ≥ 0.3% from the 18:00 open, fade back toward it (target = the 18:00
  open, stop = 1.5× the distance); flat 02:00.
**Prop-firm scoring** (typical $50k evaluation): profit target +$3,000; fail when equity is ≤ $2,000 below its highest
end-of-day balance (the trailing stop stops trailing once it reaches the starting balance) or on any day losing ≥ $1,000;
at most 60 trading days. An account is started every Monday in the period. Reported: pass rate, days to pass, and expected
value per attempt = pass rate × the first funded month's average profit (90% split, conditional on surviving) − $150 of fees.
**Pass.** Holdout expectancy per trade > 0 with t ≥ 2, holdout prop pass rate ≥ 50%, and expected value per attempt > 0.

## Result (2026-11-17): **0 of 10 pass** (`reports/ROUND52.md`)
Every NY and Asia setup lost money or was flat in 2021+ after costs (best: Nasdaq first-hour trend +0.04R, t 0.66). Prop
pass rates 0–7%, and the expected value per attempt is about −$150 (the fees).
