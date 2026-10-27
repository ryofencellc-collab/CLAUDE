# Round 15 pre-registration: Kalshi weather "first money in" (speed vs slow prices)

Written 2026-10-27, before any Round 15 code ran on real data.

## The owner's idea

Be in before slower traders react. In stocks and crypto the price is set by
high-frequency firms reacting in microseconds, so being faster than a human
does not help there. In Kalshi daily-high-temperature markets, prices are
moved by people and slow bots. The answer becomes partly known during the
day, as official weather stations report the highest temperature so far.

## The edge being tested

Settlement is the official daily high, which can only be at or above the
highest reading so far. Once the running high has passed a bracket, that
bracket's outcome is decided:

| Market type (Kalshi semantics) | Decided when the running high M reaches | Decided side |
|---|---|---|
| "greater": high > f | M ≥ f + 2 °F | YES |
| "less": high < c | M ≥ c + 1 °F | NO |
| "between": f ≤ high ≤ c | M ≥ c + 2 °F | NO |

Each threshold includes a 1 °F safety margin for rounding between station
readings and the official climate report.

**Question:** after an outcome is decided, does the market still trade the
decided side below 97¢ long enough for a fast bot to buy it?

## Data

- **Markets:** every settled Kalshi daily-high market for the US cities in
  `edge/weather.py` over the last 12 months (2025-10-27 to 2026-10-26), with
  each market's official result.
- **Trades:** Kalshi's public trade history for each market that became
  decided during its day (time, price, size, which side the taker bought).
- **Observations:** Iowa Environmental Mesonet ASOS reports for the official
  station (routine, special and 5-minute reports). A reading counts as known
  only **10 minutes after its timestamp**, a conservative delay for live feeds.
- **The day** is midnight to midnight in local standard time, matching the
  NWS climate day.

## Simulated trading

A trade in the decided side, at price p ≤ 0.97 where the taker bought that
side, means that size was offered at p. We assume we capture **25%** of every
such trade, since other fast bots exist; 100% capture is reported for
reference. Profit per contract = 1 − p − Kalshi's taker fee
(`weather.fee`). Stake per trade is capped at $100.

## Pass rule (all must hold)

1. **Decided calls are right:** at least 99.5% of decided markets settle the
   decided way. Any miss is reported in full.
2. **Real money at 25% capture:** at least $2,000 profit over the 12 months.
3. **Prints often:** a profit on at least 60% of the days that had any
   opportunity, and opportunities on at least 100 distinct days.
4. **Not fading:** the last 3 months' profit at 25% capture is at least 15% of
   the 12-month total.

## Smoke test first

New York only, last 60 days. This checks the pipeline and the decided-call
accuracy before the full run.

## Prediction written now

Uncertain. The decided calls should be near 100% right. The open question is
whether cheap trades on decided outcomes still happen, or whether other bots
already take them within seconds. I lean toward a small but real edge,
mostly in less-watched cities.
