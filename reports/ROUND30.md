# Round 30: do chart indicators predict Kalshi 15-minute crypto markets beyond the price?

Rules: [PROTOCOL_ROUND30.md](../PROTOCOL_ROUND30.md). Fit 2024–2025, judged on 2026-01..10.

## BTC

Samples: dev 280,601, holdout 116,675.

| | price only (A) | price + indicators (B) |
|---|---:|---:|
| holdout log-loss (lower = better) | 0.51395 | 0.51372 |
| holdout accuracy | 73.94% | 73.87% |

Betting where B disagrees with the price by > 2.75c, $10 a bet, 2026: **15,299 bets, win rate 54.8%, P&L $-431.83 ($-1.42/day)**; before fees and spread $7,608.88.

Indicators do not meaningfully improve on the price alone (log-loss gain +0.00024; > 0.0005 counts). Model B weights: {'z': 1.873, 'z3': -0.233, 'minute': -0.003, 'rsi2': 0.065, 'rsi7': -0.123, 'st_dir': 0.024, 'ema_gap': -0.06, 'mom3': -0.033, 'mom5': 0.031, 'pos_in_range': 0.037}

## ETH

Samples: dev 280,700, holdout 116,714.

| | price only (A) | price + indicators (B) |
|---|---:|---:|
| holdout log-loss (lower = better) | 0.50499 | 0.50436 |
| holdout accuracy | 74.66% | 74.67% |

Betting where B disagrees with the price by > 2.75c, $10 a bet, 2026: **15,912 bets, win rate 55.6%, P&L $1,151.87 ($3.79/day)**; before fees and spread $9,601.67.

Indicators improve on the price alone (log-loss gain +0.00064; > 0.0005 counts). Model B weights: {'z': 1.918, 'z3': -0.206, 'minute': -0.003, 'rsi2': 0.012, 'rsi7': -0.144, 'st_dir': 0.025, 'ema_gap': -0.065, 'mom3': -0.014, 'mom5': 0.048, 'pos_in_range': 0.071}

