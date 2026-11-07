"""Round 32 (PROTOCOL_ROUND32.md): grid bot with honest (mark-to-market) accounting and broker margin."""
import numba
import numpy as np


@numba.njit(cache=True)
def grid(px, start, horizon, spacing_frac, levels, units, fee_pct, fee_ct, margin, capital, stop_below, recenter):
    """Run one grid from px[start] for `horizon` minutes.
    Returns realized, unrealized, equity_end, min_equity, liquidated(0/1), fills, open_positions, breakouts."""
    p0 = px[start]
    center = p0
    step = spacing_frac * p0
    held = np.zeros(levels + 1, np.bool_)      # held[i]: a long bought at level i (price center - i*step)
    realized = 0.0
    fills = 0
    breakouts = 0
    min_eq = capital
    end = min(start + horizon, len(px) - 1)
    last = p0
    for t in range(start + 1, end + 1):
        p = px[t]
        if p != p:
            continue
        # sells: a position at level i sells at level i-1's price
        for i in range(1, levels + 1):
            if held[i] and p >= center - (i - 1) * step:
                sell = center - (i - 1) * step
                buy = center - i * step
                realized += units * (sell - buy) - fee_pct * units * (sell + buy) - 2 * fee_ct
                held[i] = False
                fills += 1
        # buys: every un-held level at or above the price that the price has reached
        for i in range(1, levels + 1):
            lvl = center - i * step
            if not held[i] and p <= lvl and last > lvl:
                held[i] = True
                fills += 1
        # mark to market
        unreal = 0.0
        notional = 0.0
        n_open = 0
        for i in range(1, levels + 1):
            if held[i]:
                unreal += units * (p - (center - i * step)) - fee_pct * units * (center - i * step) - fee_ct
                notional += units * p
                n_open += 1
        eq = capital + realized + unreal
        if eq < min_eq:
            min_eq = eq
        if n_open > 0 and eq < margin * notional:                  # broker liquidates everything
            exit_fee = fee_pct * notional + fee_ct * n_open
            realized += unreal - exit_fee
            return realized, 0.0, capital + realized, min(min_eq, capital + realized), 1, fills + n_open, 0, breakouts
        if stop_below > 0 and n_open > 0 and p < center - (levels + stop_below) * step:  # stop-loss under the grid
            exit_fee = fee_pct * notional + fee_ct * n_open
            realized += unreal - exit_fee
            for i in range(1, levels + 1):
                held[i] = False
            fills += n_open
            center = p
            step = spacing_frac * p
            breakouts += 1
        elif recenter and n_open == 0 and p > center + step:
            center = p
            step = spacing_frac * p
            breakouts += 1
        last = p
    unreal = 0.0
    n_open = 0
    p = px[end]
    for i in range(1, levels + 1):
        if held[i]:
            unreal += units * (p - (center - i * step)) - fee_pct * units * (center - i * step) - fee_ct
            n_open += 1
    return realized, unreal, capital + realized + unreal, min_eq, 0, fills, n_open, breakouts
