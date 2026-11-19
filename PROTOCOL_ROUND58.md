# Round 58: mention markets vs each word's own track record (written 2026-11-18, before any results)

**Idea (autonomous backlog #62, data-only version):** Kalshi "Mentions" markets ("will <speaker> say <word>?") recur. The same series asks
about the same words event after event. The record of past settlements gives a base rate per (series, word). If prices follow gut
feeling rather than that record, a base-rate model beats them. No transcripts needed.

**Data.** All 487 Mentions-like series found by `probe_mention.py`.
- **Markets:** every settled market 2025-01 → now.
- **Words:** the word key is `yes_sub_title`, lower-cased with spaces stripped.
- **Prices:** the market's trades. YES is bought at taker-YES trade prices, NO at taker-NO trade prices.

**Model.** For a market in event e of series s with word w:
- **Base rate:** prior = (yes + 1) / (n + 2) over all **earlier** events of the same series where the same word settled. Require n ≥ 3.
- **Price:** the first ask-side trade per side at least 1 hour after the market opened.

**Trade.** Buy YES if prior − ask ≥ e, or buy NO if (1 − prior) − no_ask ≥ e. 1 contract each, with the Kalshi taker fee.

**Dev/holdout.** The split is by close time: dev before 2026-07-01, holdout from 2026-07-01 → now.
- On dev, pick e ∈ {0.05, 0.10, 0.15, 0.20, 0.30} and n_min ∈ {3, 5} by mean P&L, requiring ≥ 50 dev trades.
- **Pass (holdout):** all of
  1. ≥ 100 trades;
  2. mean P&L > 0;
  3. t ≥ 2.5, clustered by event;
  4. prior Brier < market Brier on the traded markets.

**Calibration.**
- **Planted:** a synthetic world where each word has a stable rate and prices are shrunk halfway to 50¢. It must pass.
- **Null:** prices equal the true rate plus noise. It must not pass.

**Side note (not part of the pass):** Round 45b found Mentions 85–95¢ maker bids in the last hour passing on holdout (+7.3%/$).
That cell is not in the Round 46 forward test. It is noted for the promotion queue.

## Amendment 1 (2026-11-18, before any P&L was seen)
The first run produced **no dev trades at all**. The live `/markets` endpoint returned only markets from 2026-04-11 onward, so almost no
word had 3 earlier settlements before the fixed 2026-07-01 split. No P&L was computed. Two changes:
1. **More history:** markets now come from both the live and the `/historical/markets` endpoints (`edge.round20.markets`).
2. **Data-driven split:** SPLIT = the median event close among markets that have n ≥ 3 earlier settlements and at least one ask-side trade.
   That keeps dev and holdout equal in eligible size. It is chosen from the data's shape only, never from returns.

Every other rule is unchanged.

## Amendment 2 (2026-11-18, before any P&L was seen)
Run 3 spent more than 4 hours only *listing* markets (the historical endpoint pages slowly) and was cancelled. Two changes:
- **Traded series only:** list only series with traded volume in the probe, largest first.
- **Capped listing:** cap the listing phase at 40% of the time budget.

No result was computed. The rules are unchanged.

## Amendment 3 (2026-11-18, before any P&L was seen)
Run 4 died after 4.5 hours of collecting, probably out of memory from holding raw trades for every market. Collection is restructured:
1. List the markets.
2. Compute each word's history.
3. Fetch trades only for markets with n ≥ 3 earlier settlements.
4. Keep only the two first-ask prices per market, with checkpoints.

The rules are unchanged.

## Amendment 4 (2026-11-18, before any P&L was seen)
Look-ahead fix. A word's record now counts only earlier events that had **settled before the decision time** (market open + 1 h).
Before this, it counted events settled before the current event's close, which can be after the decision. This was found while auditing
Round 46m's hindsight close times. It applies to run 5, which is in flight. If run 5 finishes on the old code, it is discarded and rerun.

## Result (2026-11-19, run 6 with amendments 1–4): **FAIL on the pre-registered rule, with a strong profit signal**
- **Sample:** 44,043 settled mention markets in 212 series; 24,796 had ≥ 3 earlier settlements of the same word.
- **Dev choice:** edge ≥ 0.30, n_min 3. The split fell at 2026-06-16.
- **Holdout:** **1,759 trades, +$0.062 per contract after fees, event-clustered t 5.15.** Both sides were positive (YES +9.3¢, NO +3.6¢).
- **Why it fails:** on the traded markets the price's Brier score (0.188) beat the prior's (0.302). That condition was pre-registered, so the verdict is FAIL.
- **Reading:** the trade makes money without the base rate being the better forecaster. The edge comes from the market overreacting away from the
  word's record. When the record and the price disagree by ≥ 30¢, betting on the record's side wins on average, even though the record alone
  forecasts worse. That is a hypothesis, not a proof. Profit was concentrated in KXWCMENTION, Mamdani, Bernie and Last Word, while Trump-B, World
  News and Hearing were flat or negative.

## Round 58f (registered 2026-11-19 02:40 UTC, before any of its data exists): live paper forward test
Same rule on **new** markets only, from now on.
- **Entry:** for each open mention market at least 1 h after it opened, compute the word's prior from settlements before now. Paper-buy 1 contract at the live ask
  if prior − ask ≥ 0.30 (YES) or (1 − prior) − no_ask ≥ 0.30 (NO). One trade per market, Kalshi taker fee.
- **Pass:** after 30 calendar days, ≥ 150 settled trades, mean P&L > 0 and event-clustered t ≥ 2.
- A pass makes it a real-money candidate, subject to a budget set by the user.
