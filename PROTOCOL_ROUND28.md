# Round 28 pre-registration: live queue survey of the Round 27 candidates

Written 2026-11-07, before it runs.

**Series (fixed):** control/r28_series.json — Round 27's confirmed whole-cent series, top 80 by holdout
$ × weight (158 of 192 are sports), plus hourly crypto KXBTCD and KXETHD as controls.

**Method (edge/round28.py):** every minute, list open markets. The first time a side's best bid reaches 98c,
paper-join at 99c behind everything already resting there (size from the market listing). After the close,
count long-shot trades at 1–2c after we joined; we fill FIFO behind the queue, up to 1,000 contracts. P&L +1c
per contract if right, −99c if wrong, minus maker fee. No cancel rule.

**Window:** 7 days from the first run (2026-11-07 → 2026-11-14).

**A series passes if:** P&L > $0 over ≥ 10 joined markets with fills, and no filled wrong call (each costs
~99 wins). Passing series get their own forward test with a cancel rule before any money.

**Prediction written now:** most sports series fail on queue (incumbent market makers sit at 99c) or on a filled
wrong call (late comebacks); hourly crypto passes less well here than with the z-model entry, because joining
at 98c is later than the model.
