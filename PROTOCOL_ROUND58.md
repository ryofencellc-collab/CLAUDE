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
