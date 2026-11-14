# Round 50 pre-registration: trading Reddit crowd emotion (WallStreetBets attention)

Written 2026-11-14, before any data is collected.

**Data (no reddit.com access needed).** ApeWisdom's free API, which counts ticker mentions and upvotes on
r/wallstreetbets and other trading subreddits over a rolling 24 h, with the count 24 h earlier. A collector saves every
page of the "all-stocks" and "wallstreetbets" lists hourly (`data/wsb/`). Daily closes come from Yahoo. Historical
datasets (Hugging Face/Kaggle WallStreetBets dumps) are probed separately for a backtest.

**Signals** (each trading day, from the last snapshot at or before 15:00 ET, "all-stocks" list, US tickers with Yahoo
prices ≥ $5): surge = mentions / max(mentions_24h_ago, 10), among tickers with ≥ 50 mentions.
- A1 hype momentum: buy the top 10 by surge at the close, hold 1 day, equal weight.
- A2 the same, hold 5 days (overlapping 1/5 sleeves).
- A3 hype fade: short the A1 basket for 1 day (paper only; shows whether the crowd is wrong).
- A4 most-mentioned: top 10 by raw mentions, hold 5 days.
- A5 approval: top 10 by upvotes per mention (≥ 50 mentions), hold 5 days.
Costs 0.10% per side. Benchmark SPY.
**Pass (after 40 trading days of forward data):** mean daily excess over SPY > 0 with t ≥ 2, annualized return ≥ 15%,
worst drop ≥ −25%. Ranked by ROI, reported weekly. A historical backtest, if a usable dataset exists, uses the same
rules and is reported beside it.
