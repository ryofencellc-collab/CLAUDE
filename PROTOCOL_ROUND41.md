# Round 41 pre-registration: can a fast "price is moving at us" cancel dodge the adversely selected fills?

Written 2026-11-09, after Round 40 (filled 99c bids lost 3.21% of contracts vs a 0.05–0.10% base rate), before any of
this data is fetched.

**Idea.** A 99c bid only fills when someone sells the long shot hard, which tends to happen while the price is already
running at the strike. If the losing flow comes after a visible move and the winning flow comes in calm minutes, a
cancel rule that reacts to the last 1–5 minutes keeps the wins and skips the crashes.

**Data.** Every settled KXBTCD and KXETHD hourly market closing 2026-05-01 → 2026-11-09 (live + historical endpoints)
and every trade in its last hour; Coinbase 1-minute candles. Dev: May–Aug. Holdout: Sep 1 → Nov 9. Hours are processed
in a fixed random order within a time budget, so a cut-off run is still a random sample.
**Flow.** A trade fills a 99c bid on side s when its taker bought the other side at 1–2c. Each flow trade is stamped
with what the bot could know at that moment, from the last completed minute m before the trade: z_s (spot vs strike,
σ = std of the last 60 1-minute log returns), minutes left, the 1-minute and 5-minute moves in σ units signed so that
negative = toward the strike (d1, d5), and z_s one minute earlier (a polling lag).
**Rules scored** (flow a bid would meet, volume-weighted; the queue is ignored, so these are shares of the flow):
- base z ≥ 6; base with a one-minute lag (z one minute earlier ≥ 6);
- stricter z ≥ 8, 10, 15, 20;
- momentum guards: z ≥ 6 and d1 > −k (k = 1, 2, 3); z ≥ 6 and d5 > −k·√5 (k = 1, 2);
- timing: z ≥ 6 and ≤ 15 minutes left; z ≥ 6 and ≥ 30 minutes left.
**Reported:** flow, loss rate L = lost flow / flow, cents per contract (1·(1−L) − 99·L − maker fee), losing hours, by period.
**Sanity check.** Base-with-lag on Oct 29 → Nov 9 should land near the paper's 3.21%.
**Pass.** L < 0.5% in dev and holdout, cents per contract > 0 in both, and ≥ 25% of the base rule's flow kept.
A passing rule then runs as a forward paper variant beside the current one; it is not funded on this test alone.

## Result (2026-11-09): **not valid — the sanity check failed** (`reports/ROUND41.md`, `reports/ROUND41B.md`)
Ignoring the queue, the loss share of the flow at z ≥ 6 is 0.03% (dev) / 0.27% (holdout), and every rule formally
"passes". But the pre-registered sanity check fails: on Oct 29 → Nov 9 the method gives 0.77% where the paper bot
actually lost 3.21%, and the time-budgeted random sample (835 of 3,586 BTC hours) did not include the Nov 8 22:00 crash
hour. The no-queue method therefore understates what *our* bids meet. 41b adds the queue in front of us: at the
queue sizes the paper bot really faced (~18–20k contracts), our fills almost vanish, to tens of dollars over two months.
So the 99c bid is either tiny (behind the queue) or exposed to crash flow (when the queue is thin). Neither can prove
anything within weeks. **The 99c line of work is closed.**
