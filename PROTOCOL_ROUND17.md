# Round 17 pre-registration: sweep decided Kalshi weather outcomes at up to 99c

Written 2026-10-28, before any Round 17 run. It builds on Round 15, where all
7,619 calls flagged "decided" during the day settled the way they were called.
Few traded under 97c, but many keep trading at 98–99c for hours.

## The trade

Use Round 15's decision rule unchanged (station running high plus the 1 °F
margin, 10-minute data delay). Then buy the decided side at **up to 99c**.
It pays $1 at settlement, usually the same evening or the next morning. After
Kalshi's taker fee, profit is about 0.9c per contract at 99c, and more below
that.

## Why it could work, and how it could fail

- It works if the decided calls stay right. Break-even accuracy at 99c is
  about 99.1%. Round 15 measured 100% over 7,619 calls.
- It fails if:
  - one wrong call costs ~99c per contract;
  - Kalshi settles off a revised climate report;
  - there's too little volume to matter.

## Simulation (same as Round 15 except the price cap)

Every trade after the decision was knowable, where the taker bought the
decided side at ≤ 99c, counts as liquidity that existed. We book **25%** of
each such trade (100% is shown for reference), capped at $100 a trade, net
of the taker fee. Window: the last 12 months, 22 US cities.

## Pass rule (identical to Round 15)

1. At least 99.5% of decided calls right
2. At least $2,000 profit at 25% capture over 12 months
3. A profit on at least 60% of opportunity days, with at least 100 such days
4. The last 3 months bring at least 15% of the 12-month total

If it passes, the next step is a live paper bot. It will use Kalshi's live
order book (real asks and depth), not past trades, for at least 30 days before
any money is used.

## Prediction written now

Probably PASS on accuracy and on days, but profit is uncertain. 99c trades may
be small or rare. A rough capacity guess is $5–$30 a day at 25% capture.
