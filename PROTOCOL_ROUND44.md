# Round 44 pre-registration: earning Kalshi liquidity-incentive rewards (paper market making)

Written 2026-11-09, after reading the program rules (`probe/lip/report.json`, help.kalshi.com article 13823851) and one
snapshot of 150 programs, before any forward data.

**What it is.** Kalshi pays a daily pool (about 4,000 live programs, ≈ $84k/day in total today) to resting orders near
the top of the book. Every second it finds a reference price per side (the first level where cumulative bids reach 1/5
of the target size) and scores each order within the first target-size contracts: size × discount^(ticks below the
reference). Our reward per snapshot = pool / snapshots × (our YES-side share + our NO-side share) / 2, and only
snapshots where both sides reach the target count. The rewards are known. The risk is inventory: resting bids get
filled, sometimes by people who know more than we do.

**Strategy (fixed).** $10,000 budget. Every hour, rank live programs on `linear_cent` markets that are open, close
more than 24 h from now, and have mid between 5c and 95c, by estimated reward per dollar of collateral for
Q = 30% of the target size per side, quoted at the reference price on both sides (YES bid and NO bid). Take markets
greedily until the collateral (resting bids + held inventory) reaches $10k. Every minute: re-peg both bids to the
current reference price (we go to the back of the queue), accrue the reward share from the live book, and fill us from
the public trade tape (a trade at our price fills us only after the queue that was ahead of us; a trade through our
price fills us in full). Inventory: never more than Q contracts net long on one side. A YES + NO pair is netted to
$1 (realised spread). Unpaired inventory is marked at mid and settled at the result. Maker fee 0.0175·p(1−p) per
fill (charged even where the series has none). A dropped market keeps its inventory until it settles.

**Reported daily:** reward accrued, fills, realised spread P&L, inventory marked-to-market, settled P&L, net, capital.
**Pass (after 10 calendar days):** net P&L (reward + inventory, marked at mid, settled where settled) > 0 on ≥ 7 of
10 days, total net ≥ $300 (about 1% a week on $10k), worst day ≥ −$300, and reward ≥ 2 × inventory losses.
**Known gaps:** competitors re-pegging faster than once a minute, rewards for snapshots between our minute samples,
real queue position, and whether rewards actually pay out as estimated. All of those are settled by a small live test,
which needs the Kalshi API key and is outside this paper test.

## Amendment 1 (2026-11-09, after a 20-minute smoke run, before the forward test starts)
The smoke run worked: 65 markets quoted, $9.8k collateral, about $0.40 of reward a minute, no fills. Most of it sat in
Rotten Tomatoes score ladders (KXRT): several strikes of one film, which all move at once when the score is revealed.
Per the Nov 8 lesson (correlated strikes are one bet), each event is now capped at 3 markets and $1,500 of collateral.
The smoke ledger is discarded. Everything else is unchanged.

## Amendment 2 (2026-11-09 18:00 UTC): bookkeeping fix, no rule change
Each hourly re-rank rebuilt the record of every market it kept, so the running reward reset to zero for those markets
(the logged total fell from $15.77 to $3.58 at 16:14 and from $17.48 to $4.08 at 17:14). Kept markets now keep their
record, and markets we stop quoting bank their reward, realised P&L and fees. The rewards lost before the fix are
recovered from the per-minute log (every fall in the running total, $31.97) and carried in the bank.
