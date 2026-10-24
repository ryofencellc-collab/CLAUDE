# Round 5 pre-registration: Kalshi daily-high temperature markets

Written 2026-10-24 before any Kalshi price history was analysed (one probe
response for one market was seen while checking that the API works).

## Hypothesis

Kalshi's "Highest temperature in <city> today" contracts are priced mostly by
retail traders. Free numerical weather forecasts (GFS via Open-Meteo,
archived "previous run" values so there's no look-ahead), turned into
probabilities with each city's historical forecast error, price these
contracts better than the market does.

## Data

- Markets: every Kalshi series whose title is a daily highest temperature for
  a city (`KXHIGH*` / `HIGH*`), all settled events available from the API.
  Settlement uses Kalshi's own `result` field.
- Prices: hourly candlesticks; buying YES costs the `yes_ask` close, buying NO
  costs `1 − yes_bid` close, at the decision hour. Markets with no quote at
  that hour are skipped.
- Forecast: Open-Meteo `previous-runs` API, `temperature_2m_previous_day1`
  (GFS seamless), max over the target day's local hours. Every run feeding it
  is published before 04:00 local on the target day.
- Observed: NOAA GHCN daily TMAX at the settlement station (used only to
  measure forecast error, never to trade).

## Rule

- Decision time: **09:00 local time on the target day**, one decision per
  market.
- Model: P(high > k) = 1 − Φ((k + 0.5 − (f + bias)) / σ), using each city's
  bias and σ of (observed − forecast) estimated on the **in-sample period
  only**. "Between a and b" brackets get the difference of two such terms.
- Bet $10 on a side when model probability − price ≥ `edge`.
- Fees: Kalshi taker fee, ceil-to-cent of 0.07 × contracts × P × (1 − P),
  charged on entry. Contracts are held to settlement.
- Grid: edge {0.05, 0.10, 0.15} × `per_event` {best: only the single biggest
  edge in each city-day, all: every qualifying bracket} = **6 trials**.
  Cumulative trials across the experiment: 171 + 6 = **177**.

## Split

In-sample = all settled events except the last 120 days; holdout = the last
120 days. Bias/σ and the config choice (best IS ROI) use in-sample only.

## Pass

Holdout ROI > 0, bootstrap p × 177 < 0.05, in-sample ROI > 0, ≥ 300 holdout
bets. Win rate, % green days and $ P&L are reported for every config.

## Known limits, stated now

Candlestick ask/bid is top-of-book with unknown size; $10 bets are assumed
to fill. Settlement via The Weather Company can differ by a degree from
NOAA, which adds noise to σ but no look-ahead.

## Amendment 1 (2026-10-24 15:02 UTC)

The first run (Actions 40103074875) found that Kalshi's live API returns
only the last 68 days of settled weather markets. Everything fell inside the
120-day holdout, so there was no in-sample data and the model ran
uncalibrated (bias 0, σ 3°F). That run's numbers were seen: on those 68
days the uncalibrated model lost money (−6% ROI "best", −30% "all").
Change: markets and candlesticks are also read from Kalshi's
`/historical/...` archive (markets older than its 2026-08-25 cutoff). No rule,
grid or split changes. Disclosure: the last 68 days of the holdout have now
been seen under a *different* (uncalibrated) model. The calibrated model's
results on them have not.

## Amendment 2 (2026-10-24 15:10 UTC): owner's ideas, pre-registered before any calibrated result

The amendment-1 run was cancelled before producing results, to fold in two
hypotheses from the owner. All of the following are fixed now.

**Calibration target.** Use the official settled value Kalshi publishes on
each contract (`expiration_value`) as the observed high, for every city,
instead of NOAA. It is exactly what settles the market and needs no station
mapping. (Change for the original test too, made before seeing calibrated
results.)

**5b-1: unpopular cities.** Universe "minor" = every Kalshi daily-high city
series *not* in the original 14 US cities (e.g. Trenton, San Diego,
Oklahoma City, Tokyo, London, Paris, Toronto, Mexico City, Hong Kong,
Singapore, Berlin, Mumbai, Beijing), located at the airport station in the
series ticker. Hypothesis: thinner markets are more mispriced. Forecast
units follow the market's units (°C where the rules say Celsius).

**5b-2: multiple forecast sources.** Forecast "multi" = mean of
`temperature_2m_previous_day1` across whichever of GFS, ECMWF IFS, ICON,
GEM and JMA return data for that city-day (at least 2 required). Same
no-look-ahead construction as GFS.

**Trials.** forecast {gfs, multi} × universe {major, minor} × the original
6-config grid = 24, of which gfs × major is the original Round 5 test.
New trials: 18. **Cumulative: 177 + 18 = 195**, used for every deflation.
Each of the 4 combinations selects its own config on in-sample ROI and is
judged on the holdout with the original pass rule (p × 195 < 0.05).
