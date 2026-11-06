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
| Trading by accident | LIVE needs both secrets **and** the repo variable `LIVE21` = `1`; otherwise it is DRY |
| Leaking the API key | It lives only in GitHub secrets and is never printed. Requests are signed (RSA-PSS); the signature is tested against the public key. |
| Leaking the balance (public repo) | The balance is never written to the log when keys are present, in LIVE or DRY |
| A wrong order format | The 1c self-test checks auth and format with ≤ $0.01 at risk |
| Emergency stop | Commit the file `paper/LIVE21_STOP`, or set `LIVE21` = `0` |

## What tests cannot prove (and what covers it)

1. **Kalshi's exact field names, checked live.** The docs site is blocked from this session. The fields
   were cross-checked against Kalshi's SDK documentation, the parsing accepts both cents and dollar
   strings, and the **1c self-test** confirms them against the real API.
2. **Real fills vs. paper fills.** The paper and dry-run bots model the queue from the real order book.
   Live fills will differ somewhat. The first live week at $1,000 is the measurement.
3. **A sudden crash in a coin's price.** Cancels run every ~5 s, but a jump faster than that can still
   fill a wrong-side order. The worst case is one market's stake (≤ $950 on $1,000). This is the strategy's
   inherent risk, and the reason the pause and half-size rules exist.
