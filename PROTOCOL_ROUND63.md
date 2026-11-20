# Round 63: chart #1 markets — does the incumbent repeat more often than priced? (written 2026-11-20, before any results)

**Backlog item 58** (chart/streaming nowcasts). The step-1 probe (`probe_charts.py` → `probe/charts/series.csv`) found liquid Kalshi rank-list series:
- daily US Spotify #1 (`KXSPOTIFYD`): 528 settled events, $14.7M volume;
- daily US runner-up (`KXSPOTIFY2D`) and daily global (`KXSPOTIFYGLOBALD`);
- weekly US Spotify (`KXSPOTIFYW`);
- Billboard Hot 100 #1 (`KXTOPSONG`) and Billboard 200 #1 (`KXTOPALBUM`);
- Netflix show and movie rankings (`KXNETFLIXRANKSHOW`, `KXNETFLIXRANKMOVIE`, plus their runner-up and global versions).

Kworb, Box Office Mojo and The Numbers are reachable. They are not used in this round (v1 uses Kalshi data only).

**Hypothesis (structural):** chart positions are very sticky; a #1 song usually stays #1 the next day. Traders may underprice the incumbent, or overprice it after
a long run. The price is tested against the incumbent's own empirical repeat rate.

## Data
For every settled market in the listed series (from 2025-01-01, live and historical endpoints):
- **winner:** the event's winner is the `yes_sub_title` of its YES-settled market;
- **incumbent:** the winner of the most recent earlier event in the same series whose close time is before this market's decision time;
- **incumbent market:** the market in this event whose `yes_sub_title` (normalised) equals the incumbent. Only these are traded; at most one per event;
- **decision price:** the first YES-taker and first NO-taker trade at least 1 hour after the market opens. This is the Round 58 convention: taker prices, which pay the
  spread;
- **prior:** for each series, the smoothed rate (repeats + 1)/(n + 2) at which earlier incumbents repeated. It counts only events closed before the
  decision time, and is computed per streak bucket (current run of 1, 2–3, or 4+ consecutive wins).

## Rule
- Buy YES on the incumbent if prior − yes_ask ≥ e.
- Buy NO if (1 − prior) − no_ask ≥ e.
- Prices must be between 0.01 and 0.99. 1 contract, with the taker fee ceil(0.07·p·(1−p)·100)/100.
- Require n ≥ n_min earlier incumbent events in that bucket.

## Dev / holdout
- **Split:** at the median event close of the eligible events. That is a data-shape split, made without looking at P&L.
- **Dev grid:** e ∈ {0.05, 0.10, 0.15, 0.20, 0.30} × n_min ∈ {5, 10}. Pick the best dev mean P&L among configurations with ≥ 50 dev trades.
- **Holdout PASS requires all of:**
  - ≥ 100 trades;
  - mean P&L > 0;
  - event-clustered t ≥ 2.5;
  - Brier of the prior < Brier of the price, on the traded markets.
- **A PASS goes to a live paper forward test.** It uses the same rule, real asks and 30 days, like 58f.

## Calibration (synthetic, before any real run)
Synthetic world:
- 3 series, about 300 daily events each;
- the true repeat probability depends on streak length;
- the planted world prices the incumbent at 0.5 + 0.5·(p − 0.5), which shrinks it toward 50%; the null world prices it at p.

**Required:** planted → PASS; null → FAIL.

## Result (2026-11-20): **FAIL**
- **Data:** 31,779 settled markets in 11 series; 1,904 incumbent markets, 1,646 of them priced.
- **Dev choice:** e 0.30, n_min 10.
- **Holdout:** 187 trades, mean −$0.007 per contract, t −0.28.
- **Brier:** prior 0.379 vs price 0.130. The market is far more accurate than the repeat-rate prior.
- **Reading:**
  - Kalshi prices track the incumbents' real repeat rates closely. Spotify daily 4+ streak: 82% repeat vs 81¢; global 88% vs 85¢.
  - A new #1 (streak 1) looks overpriced by about 10¢ in most series, but in the holdout that slice made +$0.004 per contract, so the costs eat it.
  - No edge. Next for backlog 58: a real nowcast from kworb daily stream counts (the gap between #1 and #2), not raw persistence.
