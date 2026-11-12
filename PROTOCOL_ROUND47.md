# Round 47 pre-registration: rule-based strategies from published Claude trading skills

Written 2026-11-12, before any data is run. Sources are the rule descriptions in community Claude skill packs
(tradermonty/claude-trading-skills, agiprolabs/claude-trading-skills); their code is not run, and the rules are rebuilt
here. The prediction-market "longshot fade, maker side" skill matches Round 45/46 and is already in forward test.

**Data.** Round 38's US stock panel (NASDAQ Trader universe, Yahoo, adjusted OHLC, real traded price for filters),
tradable when real price ≥ $10 and 20-day dollar volume ≥ $20M. SPY from Yahoo. Dev 2015–2021, holdout 2022 → 2026-10.
Costs 0.10% per side. Signals at the close; entries at the next open. A stop is checked against each day's low (a gap
through the stop fills at the open). A same-day stop and target count as the stop.

**Rules.**
- **S1 Stockbee momentum burst:** close ≥ +4% vs prior close, volume > prior day and ≥ 100k, close in the top 30% of
  the day's range, prior day's change ≤ +2%. Stop at the burst day's low. Exit at the close of day 3 (S1a) or day 5 (S1b).
- **S2 Stockbee exhaustion hammer:** uptrend (close > 50-day average > 200-day average), pulled back ≥ 8% from the
  20-day high, today undercuts yesterday's low and closes above it, in the top 30% of the range, volume ≥ 1.2× its
  20-day average. Stop at today's low, target +2R, else exit after 10 days.
- **S3 Earnings-gap drift (PEAD proxy, no earnings calendar):** open ≥ +5% above prior close, volume ≥ 3× its 50-day
  average, close ≥ open. Stop at the gap day's low. Exit after 20 days (S3a) or 60 days (S3b).
- **S5 O'Neil follow-through / distribution-day timing on SPY:** a rally attempt starts at the first up close after
  a 25-day low. A follow-through day is attempt day ≥ 4 with a gain ≥ 1.25% on higher volume than the prior day:
  then hold SPY. Go to cash when distribution days (down ≥ 0.2% on higher volume) reach 5 within 25 sessions.
**Portfolio (S1–S3).** Each day take up to 5 new signals ranked by volume ratio, 10% of equity each, at most 10 open.
**Pass.** S1–S3: holdout mean net return per trade ≥ +0.3%, t ≥ 3 (clustered by entry date), dev mean > 0, holdout
portfolio CAGR ≥ 15% and Sharpe ≥ 1. S5: holdout Sharpe above SPY buy-and-hold and worst drawdown shallower. A pass goes
to forward paper; nothing is funded on a backtest alone.
