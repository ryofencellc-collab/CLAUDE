# Blind test: can the system find a strategy hidden in fake data? (written 2026-11-17, before any analysis)

The user asked for this: 3 fake 1-minute sources (X, Y, Z), 2 years each (2024-01-02 → 2025-12-31). `gen_blind.py` planted ONE
hidden strategy in ONE source. Source, strategy, parameters and strength were drawn from `os.urandom` and written only to
`data/blind/secret.json` (not committed, and not read by the analyst until both detectors below have run).

**Commitment:** `sha256(secret.json) = a7ddf61213c9b76403cc865b43d1f4582c9a8ac75163704c1f3209a4b42421df`.
At the reveal the file is printed and the hash re-checked, so the secret can't be changed afterwards.

The analyst knows the pool of 7 strategy types in `gen_blind.py` (it was written before the draw). Detector 2 is therefore
the weaker evidence; detector 1 is the existing system, unchanged.

## Detector 1: the Round 53 system, unchanged
`run_blind.py grid`: the exact Round 53 grid (1,728 configurations per source), costs as for the S&P micro. Dev = 2024 and holdout = 2025.
Screen: holdout t ≥ 3 and dev t ≥ 2. The cross-market check is reported but not required, because by design the edge lives in one source.
**Guess** = the source with the most screen candidates and the family they share. The detector **fails** if no source has a candidate.

## Detector 2: generic segment scanner
`run_blind.py scan`: for each source, conditional segment-return tests:
- **Signals:** sign of the overnight, gap, first 15/30/60 minutes, open→12:00 and open→15:00 moves, the previous-day narrow
  range, and each weekday.
- **Targets:** every later segment of the session.

A test is significant at Bonferroni p < 0.05 over all tests on all 3 sources and must have the same sign in both years.

## Scoring
1. **Right source?** The false-positive check is that the two clean sources produce nothing.
2. **Right strategy type?**
3. **Bugs:** any flaw found in the system.
