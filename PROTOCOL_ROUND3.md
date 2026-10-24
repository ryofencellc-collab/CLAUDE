# Round 3 pre-registration: forward paper test of football value betting

Written 2026-10-24, **before** any Betfair-based backtest was run and before
any forward bet was logged.

## Why Round 3

Round 2's best lead: bet the best market price when it beats the sharp
"fair" line by ≥ 2%, odds ≤ 5.0. It made +3.5% ROI over 4,240 holdout bets
and +3.7% over 26,048 bets in all seasons, but did not pass (p = 0.08 before
deflation; not the variant the selection rule picked).

## Forced change: the sharp reference

The Round 2 rule used Pinnacle's odds as the fair line. football-data.co.uk
stopped publishing Pinnacle odds during 2025/26 (only 322 bets that season),
and the live 2026/27 feed has none. The feed **does** carry Betfair Exchange
back prices (`BFEH/BFED/BFEA`). An exchange is the other standard sharp
reference.

**Frozen rule (no parameters to tune):**
- Fair probability = Betfair Exchange back prices, de-vigged proportionally.
- Bet an outcome (home/draw/away) when the best market price (`Max`) is
  ≥ fair odds × 1.02 and ≤ 5.0.
- $10 flat stake per bet, $1,000 paper bankroll. Only the first qualifying
  price seen for each match/outcome is logged, and only ≥ 30 minutes before
  kickoff. Same 22 leagues as Round 2.

## Step 1: feasibility backtest (does the Betfair line behave like Pinnacle?)

Run once on history where both `Max` and `BFE` columns exist. Reported:
ROI per season, in-sample (seasons before 2022/23) vs holdout (2022/23 on),
and the overlap with the Pinnacle-based bets. **Go** for the forward test
if holdout ROI > 0. **No go** (the experiment's betting track ends) if
holdout ROI ≤ 0. This is a feasibility gate, not proof: proof can only come
from the forward test.

## Step 2: forward paper test (the actual test)

- A scheduled GitHub Actions job pulls the live fixtures feed twice a day,
  logs qualifying bets to `paper/bets.csv`, and settles them from published
  results. Every bet is committed to git before kickoff.
- Minimum duration 60 days **and** ≥ 200 settled bets.
- **Pass:** paper ROI > 0 **and** paper ROI is above the 5th percentile of
  what the backtest predicts for that many bets. With per-bet standard deviation
  1.62 (Round 2 holdout), that floor is 3.5% − 1.645 × 1.62 / √n; for n = 300
  it is −11.9%.

Honest limit, stated in advance: 60 days (~300 bets) **cannot** prove a 3.5%
edge. One standard error is about ±9.4%. It can catch a broken rule or a
dead edge. It can't confirm a live one. Confirming +3.5% at 2σ would take
about 8,000 bets, roughly 7 seasons.

## Bankroll warning, from the Round 2 numbers

At $10 stakes on a $1,000 bankroll, the worst historical drawdown was
**−$1,567** (all seasons) and −$912 (holdout). $10 stakes would have
bankrupted a $1,000 account at least once. Any live phase must use stakes
≤ 0.5% of bankroll ($5 on $1,000), or a larger bankroll.

## Step 1 result (run 40100116520, 2026-10-24)

Betfair + Max odds exist only for 2024/25 and 2025/26 (14,764 matches).
Betfair-referenced rule: **3,054 bets, +1.17% ROI, +$355.80 at $10 stakes,
max drawdown −$802** (2024/25 −1.0%, 2025/26 +5.2%). It overlaps with the
Pinnacle rule on 712 of 1,514 Pinnacle bets in the same matches.
**Gate: GO.** The edge looks about a third as large as the Pinnacle version.
Forward paper test started.

## Amendment 1 (2026-10-24 14:05 UTC, before any forward bet settled)

The first forward run logged 15 bets. 5 came from illiquid exchange markets
quoting junk prices (e.g. 1.11/1.13/1.16 on all three outcomes, a 265% book),
which make the de-vigged "fair" odds meaningless and create fake edges of up
to 58%. Data-quality rule added: use the Betfair line only when its
three-way book is between 97% and 106%. The 5 bets are voided (stake
returned, excluded from results) before their matches kick off. The
feasibility backtest is re-run with the same rule and its result recorded
below, GO or NO GO.
