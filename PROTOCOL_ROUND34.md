# Round 34: whale autopsy — what do Polymarket's most profitable wallets actually do?

Written 2026-11-07. Polymarket trades are on-chain, so every wallet's history is public. Telonex's study of one
week of 15-minute crypto markets (46,945 wallets) found makers netted +$728k while takers lost, with two
winning archetypes: 100%-maker bots across thousands of markets, and a few "snipers".

## Method (run_round34.py, Polymarket Data API v2)

1. Leaderboards (top 100 by PnL) for this month and all time, overall and by category where available.
2. For each wallet: its last ≤ 3,000 trades and ≤ 1,000 activity rows (activity shows maker rebates).
3. Per wallet: markets, trades/day, hours active (bot vs human), trade size, share of buys at ≥ 90c / ≤ 10c /
   in between, share of markets where it bought both outcomes, category mix (crypto up/down, other crypto,
   sports, politics, weather, other), timing before the end for crypto up/down markets (end time is in the slug),
   maker-rebate count.
4. Archetypes by fixed rules (below); PnL per archetype; deep profiles of the top 15.

Archetype rules (first match): **market maker** (both outcomes in ≥ 40% of markets, or any maker rebates, and
≥ 200 markets); **sniper** (< 30 markets); **late-favourite closer** (≥ 50% of buys at ≥ 90c);
**long-shot buyer** (≥ 40% of buys at ≤ 10c); **specialist** (one category ≥ 70% of trades); else **mixed**.

This is description, not a backtest: it tells us what to build next; anything we build is then tested.
