# Round 23 pre-registration: the portfolio, with a risk engine

Written 2026-11-01, before any of the data it is judged on exists.

## The idea

Successful systematic shops (CTAs, multi-strategy funds, market makers) do
not rely on one trade. They run several small, unrelated edges at once, each
with hard limits, so no single failure ends the account. Out of about 300
trials, three edges are still alive, and they share no common driver:

| Sleeve | Capital | Edge | Driver |
|---|---:|---|---|
| A | $5,000 | Round 21/22: 99c bids on Kalshi 15-minute crypto markets already decided by the spot price, **2,500 contracts** per market | lottery-ticket flow on Kalshi |
| B | $4,000 | Round 13: SPY core + multi-asset trend + crypto trend | stock, bond, commodity and crypto trends |
| C | $1,000 | Round 3: football value bets against Betfair-implied fair odds, flat $10 stakes | soft bookmaker prices |

Total: $10,000 on paper. Each sleeve uses its existing bot and ledger,
unchanged.

**Why 2,500 contracts for A:** at that size a single wrong fill costs
$2,475, about 25% of the account, which can be survived. 10,000 contracts
would earn more but a wrong fill would cost the whole account. On the first
2.9 live days, 2,500 contracts made about $85 a day (10,000 would have made
about $242).

## Risk engine (applied in the paper accounting, rules fixed now)

1. **A, after any losing filled market:** pause A for 24 hours, then trade
   it at half size (1,250 contracts) for 7 days.
2. **Daily stop:** if the portfolio loses more than $500 on a day, nothing
   new is booked that day. A's fills on markets that close later that day
   are dropped.
3. **Drawdown:** at −15% from the portfolio's peak, every sleeve trades at
   half size. At −25%, everything stops pending review.
4. **Sleeve gates:** a sleeve whose own pre-registered forward gate fails is
   switched off from the day it fails.

## Window

2026-11-01 to 2026-11-30 (30 days). A is booked by market close date, B by
trading day, and C by settlement date.

## Pass rule (all must hold)

1. Portfolio profit ≥ $1,500 (≈ $50/day, 15% in a month).
2. Max drawdown from peak ≤ 15%.
3. Profitable on ≥ 60% of days with any P&L.
4. At least 2 of the 3 sleeves are net positive.

## Prediction written now

PASS, with A carrying it at about $60–90/day. B is roughly flat over one
month, and C is noise at this stake size. The main risk is a wrong filled
call in A.
