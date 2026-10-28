# Round 16 (not run): Kalshi vs Polymarket same-game arbitrage

Dropped after a data check (`probe16.yml`, `probe16b.py`), before any test:

- **Fees:** the only Polymarket a US person may use is Polymarket US. Its
  sports taker fee (about 5%) plus Kalshi's (~1.75c at 50c) leaves about 4c of
  every $1 to fees, so a gap must beat ~4c before there is any profit.
- **Access:** the global Polymarket, where most of the liquidity is, is closed
  to US persons.
- **Matching:** global Polymarket's tag listings returned season-long markets,
  not single games, so the two venues did not line up cleanly.

Not counted as a trial, since no strategy was evaluated.
