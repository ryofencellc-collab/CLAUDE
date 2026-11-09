# Live trader audit (edge/live21.py): every way it could lose the $1,000, and what stops it

Audited 2026-11-06. Each guard is proven by an automated test (`tests/test_live21.py`,
`tests/test_live21_scenarios.py`). The scenario tests run the trader against a simulated Kalshi exchange
and a controllable clock. The full suite has 97 tests, all passing.

## Losing money on a trade

| Risk | Guard | Test |
|---|---|---|
| Paying more than 99c, or crossing the spread | Post-only limit buy at 99c only; Kalshi rejects it if it would take liquidity | `test_order_is_post_only_99c_limit_buy` |
| The price swings back after we bid | Every ~5 s: cancel if z < 6 | `test_reversal_cancels_and_a_loss_pauses_then_halves` |
| Acting on an old or broken price | Coinbase candles older than 3 min, or under 30 min of history: treated as no data, so the order is pulled and nothing is placed | `test_stale_spot_pulls_the_order` |
| A loss followed by another | 24 h pause, then half size for 7 days | `test_reversal_cancels_and_a_loss_pauses_then_halves` |
| A bad day | No new orders after losing 10% of the day's starting balance; losses come from Kalshi's own settlement records | `test_daily_stop_from_settlements` |
| Two positions at once | One order or position at a time; none while any earlier position is open | `test_restart_with_leftovers_sweeps_blocks_and_learns_the_loss` |
| Trading the same market twice | A market is never traded again once ordered (a rejected order doesn't count) | `test_winning_market_end_to_end`, `test_rejected_order_cools_down_instead_of_hammering` |
| Betting more than the account | Size = min(cap, 95% of the live balance / 0.99) | `test_small_balance_sizes_down` |

## The bot losing track of an order

| Risk | Guard | Test |
|---|---|---|
| An error right after placing | The order is saved to state before anything else runs | `test_live_tracks_order_and_redacts_balance` |
| A rejected order | Nothing tracked, and a 60 s cool-down so it doesn't hammer the API | `test_rejected_order_leaves_nothing_tracked`, `test_rejected_order_cools_down_instead_of_hammering` |
| Orders we don't know about | A sweep every 30 s cancels them. Orders you place by hand are never touched. | `test_sweep_cancels_only_untracked_orders_of_ours` |
| The job ends or is cancelled | Everything of ours that is resting is cancelled on exit (including on SIGTERM) | `test_job_end_cancels_anything_resting` |
| The bot dies without warning | Every order carries `expiration_ts` = market close, so Kalshi removes it within ≤ 15 minutes | `test_winning_market_end_to_end` |
| A crash loses the loss memory | Risk is rebuilt from Kalshi's settlements at start and every minute | `test_rebuild_risk_from_settlements` |
| A market never resolves (void) | It stops blocking after 3 h | `test_void_market_unblocks_after_three_hours` |
| Cancelling an already-filled order | A 404/409 from Kalshi is treated as done | `edge/live21.py` (`Kalshi.cancel`) |

## Access and secrets

| Risk | Guard |
|---|---|
| Trading by accident | LIVE needs both secrets **and** `"live": true` in Claude's `control/live21.json` **and** no owner veto (`LIVE21` = `0`). A missing or unreadable control file means stopped. |
| Leaking the API key | It lives only in GitHub secrets and is never printed. Requests are signed (RSA-PSS); the signature is tested against the public key. |
| Leaking the balance (public repo) | The balance is never written to the log when keys are present, in LIVE or DRY |
| A wrong order format | The 1c self-test checks auth and format with ≤ $0.01 at risk |
| Emergency stop | `"stop": true` in the control file. The running bot re-reads it from GitHub every minute, pulls its order and places nothing more. The owner's `LIVE21` = `0` also forces dry run. |
| Stake too large for a one-time $1,000 | `stake_fraction` (default 0.5, hard cap 0.95) limits one market's share of the balance |

## What tests cannot prove (and what covers it)

1. **Kalshi's exact field names, checked live.** The docs site is blocked from this session. The fields
   were cross-checked against Kalshi's SDK documentation, the parsing accepts both cents and dollar
   strings, and the **1c self-test** confirms them against the real API.
2. **Real fills vs. paper fills.** The paper and dry-run bots model the queue from the real order book.
   Live fills will differ somewhat. The first live week at $1,000 is the measurement.
3. **A sudden crash in a coin's price.** Cancels run every ~5 s, but a jump faster than that can still
   fill a wrong-side order. The worst case is one market's stake (≤ $950 on $1,000). This is the strategy's
   inherent risk, and the reason the pause and half-size rules exist.

## Failure scenarios (tests/test_live21_failures.py)

Everything that can go wrong apart from the market itself. Each scenario runs the real code against the
simulated exchange.

| Scenario | What the bot does |
|---|---|
| Kalshi goes down (503) with our order resting | Logs the error and cancels the order; nothing is left exposed |
| Rate-limited, or the API key is wrong or expired (401) | Logs errors, places nothing, keeps running |
| A cancel keeps failing | Retries every pass; the order isn't marked cancelled until it really is, and it expires at close anyway |
| An order is accepted but the response loses its id | The 30-second sweep cancels it, so nothing rests that we can't track |
| Cancelling an order that already filled (404) | Treated as done; real failures (500) still surface |
| Coinbase down, garbage response, too little history, or candles 9 minutes old | No price: bids are pulled and nothing new is placed |
| Kalshi's market list unavailable | No candidates, no orders |
| A market with missing or odd strike data | Never counts as decided |
| GitHub unreachable, so a stop could not reach the bot | Keeps the last control file through brief blips; **stops after 5 failed checks in a row** |
| Control file with corrupt values, or the wrong JSON shape | Falls back to the safe values: smallest stake, not live |
| The owner withdraws the whole balance | Sizes to 0 and logs a skip |
| Midnight UTC with a pause active | The day's loss counter resets; the 24 h pause does not |
| Corrupt state file at startup | Starts from safe defaults (bug found and fixed in this audit); in LIVE, the loss rules are rebuilt from Kalshi |
| GitHub cancels the job mid-trade (SIGTERM) | Every resting order of ours is cancelled on the way out |
| An error right after a full fill | The position is still settled and booked correctly |

**Not testable here, handled by the platform:**

- **Two jobs running at once:** prevented by the workflow's concurrency group, so at most one trader runs.
- **Kalshi's live field names:** confirmed by the 1c self-test before any live trade.

## Audit pass, Nov 7

| Finding | Fix | Test |
|---|---|---|
| Sparse high-\|z\| table cells carry a prior near 50%, so a *bigger* lead could look riskier and cancel the safest orders | `flip_risk` makes the table monotone: risk never rises as \|z\| grows (`np.minimum.accumulate` down the z axis) | `test_table_is_made_monotone_so_a_bigger_lead_is_never_riskier` |
| Settlement and fill reads stopped at one page (200 rows), so daily loss / pause could miss losses on a busy day | `Kalshi.pages()` follows the cursor; settlements read with `min_ts` | `test_settlements_and_fills_read_every_page` |
| Module docstring still described the old z ≥ 6 rule | Rewritten for the Round 25 gate and the control system | — |

## Running unattended (Nov 7)

| Risk | Guard | Test |
|---|---|---|
| RULES.md stops/stake depended on Claude editing the control file | `governor()` enforces them from Kalshi settlements every minute | `tests/test_live21_governor.py` (stake schedule, 2-in-7 halt, floor halt never wears off, errors keep last answer) |
| A halt left an already-resting order on the book | halt cancels the open order like a control stop | `test_a_halt_blocks_and_pulls_the_resting_order` |
| A halted account restarting in LIVE | startup applies the governor before choosing the mode | `test_a_halted_account_starts_in_dry_run` |
| A hung `git fetch` (control file) froze the trading loop | every git call has a time limit; a timeout counts as a missed read (5 misses = stop) | `test_a_hung_git_fetch_counts_as_a_miss_instead_of_freezing` |
| A failed `git pull --rebase` left the checkout mid-rebase | `rebase --abort`, retry at the next commit | same test |
| A run queued hours earlier started on old code and old state | checkout uses the branch tip at job start | workflow |
| Self-chain broken (dispatch failed) → up to 3 h idle | 4 dispatch retries; hourly cron backup | workflow |
| Dry run sized at the control cap (0.78) while live would use the governor's 0.5 | the governor also runs in dry run, on the paper ledger | `test_dry_run_sizes_with_the_same_rules_as_live` |
| `live_since` left blank → the account would look old and jump to 0.95 | with no live_since, days count from the first settlement | `test_a_missing_live_since_never_skips_the_first_14_days` |

## Kalshi API 3.36 migration (Nov 7) — found by reading the published spec, before any live order

| Finding (spec v3.36.0, `tests/fixtures/kalshi_openapi_3.36.yaml`) | Would have caused | Fix |
|---|---|---|
| `POST /portfolio/orders` and `DELETE /portfolio/orders/{id}` are no longer in the API (legacy, retired after May 6, 2026) | every live order and cancel failing | Create/Cancel Order V2: `POST /portfolio/events/orders`, `DELETE /portfolio/events/orders/{id}?market_ticker=` |
| V2 body: YES-book `bid`/`ask`, string `count`/`price`, required `time_in_force` + `self_trade_prevention_type`, `expiration_time` | orders rejected | `order_body` rewritten; buy NO at 99c = `ask` at 0.0100; `cancel_order_on_pause` on |
| V2 response has `order_id` at the top level (no `order` wrapper) | bot losing track of every order | `buy()` reads it, raises if missing |
| Fill `action`/`side` deprecated; a NO buy is a YES `ask` | NO fills counted as 0 | fills counted by `order_id` |
| Settlement `fee_cost` is dollars, not cents | fees 100x too small in loss rules | read as dollars |
| `balance` is whole cents; direct members carry 0.01c | small balance rounding | `balance_dollars` first |
| resting orders / positions read one page | strays beyond 200 missed | paginated |

`tests/test_live21_api_contract.py` replays every client call against the spec: path + method exist and are
not deprecated, query parameters are known, order bodies match `CreateOrderV2Request` exactly.

## Three-exchange prices (Nov 7)

Kalshi's 15-minute crypto markets settle on the CF Benchmarks Real Time Index (60-second average before the
close; the market's own `rules_primary`), built from several exchanges' trades. The trader used Coinbase alone.
`edge/prices.py` now reads Coinbase, Kraken and Bitstamp 1-minute candles:

| Rule | Why |
|---|---|
| ≥ 2 exchanges with complete candles ≤ 3 min old and ≥ 30 bars | one exchange down or lagging can't drive a bid |
| every close within 0.30% of the median, else no price (no bid; a resting bid is pulled) | a glitch on one exchange can't fake a lead; normal spread is ~1–10 bp (probe, Nov 7) |
| lead = smallest over the exchanges; vol = largest | bid only when all agree it's decided |
| the forming minute is dropped; candles sorted by time | Kraken/Bitstamp include the open minute; Coinbase lists newest first (a test caught this) |
| 10 s cache | ≤ 0.5 requests/s per exchange |

The paper bot (`edge/paper21.py`) is unchanged so Round 22 is not altered mid-window.
Tests: `tests/test_prices.py` (real saved responses, staleness, disagreement, broken data, worst-case lead).

## Unexplained cash (Nov 7)

RULES.md's "anything unexplained" stop, as code (`audit_balance`): whenever the bot holds nothing (no open
market, no resting order, no position), Kalshi cash must have moved by exactly what the settlement records say
since the previous such check (within max($1, 1%)). A mismatch lasting 10 minutes halts until a fresh start.
It catches an unrecorded deposit or withdrawal, a trade this bot did not make (e.g. a leaked key, or manual
trading on the account), and bookkeeping errors. Checked step by step so fee rounding never accumulates.
The halt message carries no dollar amounts (the log is public).
Tests: `test_unexplained_cash_change_halts_after_ten_minutes`, `test_a_brief_lag_between_cash_and_records_is_tolerated`,
`test_audit_waits_while_anything_is_open`.

Owner rule that follows: **no manual trading on this Kalshi account**, and tell Claude before any deposit or
withdrawal (Claude then sets a new `deposit` and `live_since`).

## 2026-11-09: the Nov 8 22:00 UTC crash (dry run −$157, paper −$3,846)
BTC fell from 75,330 (21:46) to 73,477 (21:55) and the CF RTI settled the 5 pm ET hour at 73,982.72 (Kalshi
`expiration_value`, checked in `probe/loss/report.json`). That is a real move, not a price-feed fault: Coinbase 1-minute
candles show it. Bids placed at z = 6.6–17.1 lost, and the sellers who filled our 99c bids were the ones dumping into
the crash, so the fills arrived exactly when the bids were wrong. The paper bot (1,000 contracts per strike, five BTC
strikes of that hour) lost $3,846 in one minute after earning +$2,160 over 11 days; it is now **−$1,685** overall.
The dry run lost three BTC strikes (−$157, 15% of the $1,000 deposit), and the governor halted it as designed
(2 losses in 7 days).

**Fix (bug): one position per coin per settlement hour** (`event_of`, `step`). Strikes of one event fail together, so
several of them are one bet several times larger than the stake schedule allows. Cancelled-but-unsettled orders count,
because they may have filled. Test: `test_one_position_per_coin_per_hour`. Replayed on the paper fills, keeping the
first-placed strike of each coin-hour gives +$1,763 instead of −$1,685. That is shown only to size the fault: which
strike gets kept is arbitrary, and it is not evidence the strategy works.

**What it does not fix:** z ≥ 6 is not "near-certain". The z-score assumes normal moves, and crypto jumps. Whether the
hourly 99c bid makes money after crashes is unknown until the empirical tail rate is measured on years of 1-minute
data. Do not fund until that is done.
