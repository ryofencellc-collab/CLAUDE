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
