# Round 65: does Polymarket lead Kalshi on Fed decisions? Hourly lead-lag (written 2026-11-20, before any results)

**Backlog item 59.** The probe (`probe/leadlag/probe_b.json`) found:
- 21 Polymarket "Fed decision in <month>" events, many with $100M+ volume;
- the matching Kalshi `KXFEDDECISION` and `KXFED` series;
- Polymarket history is available **hourly only**; Kalshi has hourly candles.

Polymarket is used only as a **signal**. All trades are on Kalshi, at Kalshi taker prices and fees. Round 16 found Polymarket itself unusable: fees, plus US access.

## Data
- **Pairs:** Polymarket Fed events matched to Kalshi `KXFEDDECISION-<YYMON>` by meeting year and month.
- **Outcomes:** matched by meaning:
  - hold ↔ "no change";
  - cut 25 ↔ "decrease 25 bps";
  - cut > 25 ↔ "decrease 50+ bps";
  - hike 25 ↔ "increase 25 bps";
  - hike > 25 ↔ "increase 50+ bps".
  Kalshi codes H0 / C25 / C26 / H25 / H26, or the market's subtitle text.
- **Kalshi:** hourly candles (live or historical endpoint), using the yes-bid and yes-ask at each candle close, plus the settlement result.
- **Polymarket:** hourly price points of the YES token.
- **Look-ahead control:** at a Kalshi decision time T (a candle close), the Polymarket price used is the latest point with timestamp ≤ **T − 1 hour**. That avoids any ambiguity about what a point's timestamp means. The test therefore asks whether Kalshi lags by more than an hour.

## Rule
At each hour T, for each matched outcome, with p = the Polymarket price:
- if p − kalshi_yes_ask ≥ g, buy YES at the ask;
- if kalshi_yes_bid − p ≥ g, buy NO at 1 − bid.

**Exit:**
- at the bid after H hours (YES at the yes-bid; NO at 1 − yes-ask);
- or at settlement (1 or 0) if the market closes first.

Fees: the Kalshi taker fee on entry and on a non-settlement exit. One open position per market at a time. 1 contract.

## Dev / holdout
- **Split:** chronological at the median meeting.
- **Grid:** g ∈ {0.02, 0.03, 0.05, 0.08} × H ∈ {1, 3, 6, 24}. Pick the best dev mean with ≥ 50 dev trades.
- **Holdout PASS requires all of:**
  - ≥ 100 trades;
  - mean P&L > 0;
  - meeting-clustered t ≥ 2.5;
  - above a **time-shift null**: the same chosen rule with the Polymarket series shifted +7 days, which destroys timing information. The real mean must exceed that
    null's mean.

## Calibration (synthetic)
Synthetic markets: a random-walk "true" probability; Kalshi quotes have a 2¢ spread.
- **Planted:** Kalshi = Polymarket lagged by 3 hours. It must PASS.
- **Null:** Kalshi and Polymarket are independent random walks. It must FAIL.

## Amendment 1 (2026-11-20, calibration only, before any real data was collected)
The first synthetic design could not be detected:
- Kalshi lagged Polymarket by 3 hours, with log-odds steps of sd 0.06 per hour;
- with the 1-hour look-ahead buffer, that leaves about a 2¢ edge, below the 2¢ spread plus fees.

The planted world now uses a 6-hour lag, and **both** worlds use steps of sd 0.15 per hour. Real-data rules are unchanged.

Calibration result: planted **PASS** (t 6.6); null **FAIL** (t −19).

## Amendment 2 (2026-11-20, data collection only; no rule change)
**First run:** 85 outcome pairs were matched, but Polymarket returned **0** history points for every resolved market (`interval=all`), so only 3 future meetings had
data. That run is a data failure, not a verdict.

**What the probe found** (`probe65.py`): resolved markets do answer `startTs`/`endTs` windows of **≤ 7 days**. With fidelity 1 that is minute-level data (about 10,000 points per week).

**Fix:** the collector now pulls hourly (fidelity 60) Polymarket history in 7-day windows over the 90 days before each meeting. The rules, grid, split and pass
criteria are unchanged.

**Follow-up idea (not part of this round):** minute-level Polymarket and Kalshi histories both exist, so a minute-level lead-lag (Round 65b) is possible. It would be
pre-registered separately.

## Amendment 3 (2026-11-20, data bugs found by per-pair diagnostics; no rule change)
1. **Kalshi price scale:** historical-endpoint candles report the close in **dollars**, but the collector divided every close by 100. Resolved meetings therefore showed about 90¢
   "gaps" and 0.01¢ spreads, and every g gave the same trades.
   Fix: the unit is detected per series (cents if any value is > 1).
2. **Duplicate pairs:** two Polymarket questions could map to one Kalshi outcome. Only the highest-volume Polymarket market per (meeting, outcome) is kept.

The rules, grid, split and pass criteria are unchanged. The earlier "FAIL (no dev config with 50 trades)" came from these bugs and is void.

## Result (2026-11-20, after amendments 2–3): **FAIL**
- **Data:** 78 matched outcome pairs with both histories, across 18 Fed meetings (2024-12 → 2027-01).
- **Dev choice:** g 0.03, H 24 h, split at the 2026-01 meeting.
- **Holdout:** 298 trades, **−$0.040 per contract**, meeting-clustered t **−5.25**. Every holdout meeting lost. The time-shift null lost about the same (−$0.048).
- **Dev:** all 16 configurations lost (−2.7¢ to −8.3¢ per contract).
- **Reading:**
  - Kalshi and Polymarket Fed prices track each other within about 1¢ hour to hour (correlation 0.94–0.99 on the main outcomes).
  - When they diverge by 2–8¢, Kalshi does **not** catch up to Polymarket within 1–24 hours by more than the spread plus fees.
  - At hourly resolution there is no exploitable lead.
- **Minute-level follow-up (65b):** possible, since both venues have minute history. It is low priority: a lead that doesn't survive one hour would have to be a sub-hour effect much
  larger than the 1¢ spread plus fees.
