# Round 19 pre-registration: the Round 18 trade on every other daily-temperature series

Written 2026-10-29, before any Round 19 code ran on real data.

## Why

Round 18 passed its backtest on 22 US daily-high series. Kalshi lists about
90 more daily series with the same structure:

- daily **low** temperature, US and international;
- daily **high** temperature for cities Round 18 skipped: Newark, San Antonio,
  and 20+ international airports.

If the same flow exists there (lottery-ticket buyers of already-decided
losers), adding it scales the strategy toward the $100/day goal.

## The trade

The trade is Round 18's, unchanged: rest a 99c bid on the decided side,
capture 25% of later fills, pay the assumed maker fee, $100 cap per fill.

For daily-high series the decided rule is Round 15's. For daily-low series,
the same rule is mirrored on the running minimum m, with the same 1° margins:

| Market (Kalshi semantics) | Decided when m reaches | Decided side |
|---|---|---|
| "greater": low > f | m ≤ f − 1 | NO |
| "less": low < c | m ≤ c − 2 | YES |
| "between": f ≤ low ≤ c | m ≤ f − 2 | NO |

For markets whose rules say Celsius, station readings are converted to °C and
the margins apply in °C, which is wider and so more conservative.

Station readings come from IEM (ASOS/METAR for each airport code). The day
runs midnight to midnight in local standard time, as before.

## Universe

Every daily series in Kalshi's "Climate and Weather" category whose ticker
resolves to a station in `edge/round19.py`, minus Round 18's series. Excluded
as ambiguous: the "SDF" series titled SATX/SDX, and the multi-city series.

## Split (the station mapping is the main risk, so it is validated first)

- **Window:** 2025-10-28 to 2026-10-27.
- **Dev (first 6 months, to 2026-04-27):** a series is eligible only if it had
  at least 10 decided markets and **every** decided call settled the decided
  way. A wrong time zone, unit or station shows up here as misses.
- **Holdout (last 6 months):** eligible series only. The verdict uses the
  holdout alone.

## Pass rule (holdout, all must hold)

1. Decided calls ≥ 99.5% right.
2. Profit at 25% capture ≥ $1,000 (half of Round 18's $2,000 bar for half the time).
3. A profit on ≥ 60% of days with any opportunity, and opportunities on ≥ 50 days.
4. Not fading: the last 3 months are ≥ 30% of the holdout total.

## Smoke test first

Four series over the last 60 days: NYC low, London high, Tokyo low and Newark
high. Accuracy check only, to confirm stations, time zones and units.

## Prediction written now

- **US lows:** a similar but smaller flow than US highs.
- **International series:** thinner trading, and some settle on sources that
  disagree with METAR, so several fail the dev accuracy screen.
- **Overall:** PASS, adding roughly $15–40/day at 25% capture.
