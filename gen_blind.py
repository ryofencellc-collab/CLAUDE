"""Blind test (PROTOCOL_BLIND.md): make 3 synthetic 1-minute index sources, 2 years each, and plant ONE hidden strategy
in ONE of them. The choice (source, strategy, parameters, strength) is drawn from os.urandom and written only to
data/blind/secret.json, which the analyst must not read until the backtests are finished. Only its SHA-256 is printed.
"""
import hashlib, json, os
import numpy as np, pandas as pd

OUT = "data/blind"
SOURCES = ["X", "Y", "Z"]
POOL = ["orb_continuation", "gap_fill", "power_hour_trend", "weekday_drift", "lunch_reversal",
        "overnight_momentum", "narrow_range_breakout"]
ON_MIN, RTH_MIN = 930, 390          # 18:00 -> 09:29 overnight, 09:30 -> 15:59 cash session


def secret_draw():
    rng = np.random.default_rng(int.from_bytes(os.urandom(8), "little"))
    kind = POOL[rng.integers(len(POOL))]
    s = dict(source=SOURCES[rng.integers(3)], strategy=kind, strength_k=round(float(rng.uniform(0.30, 0.45)), 3))
    if kind == "orb_continuation":
        s["or_minutes"] = int(rng.choice([15, 30]))
    elif kind == "gap_fill":
        s["min_gap_pct"] = round(float(rng.choice([0.2, 0.3])), 2); s["fill_minutes"] = 90
    elif kind == "weekday_drift":
        s["weekday"] = int(rng.integers(5)); s["direction"] = int(rng.choice([-1, 1]))
    elif kind == "narrow_range_breakout":
        s["or_minutes"] = 30
    return s


def u_shape():
    m = np.arange(RTH_MIN); w = 1 + 2.0 * np.exp(-m / 30) + 0.8 * np.exp(-(RTH_MIN - 1 - m) / 25)
    return w / np.sqrt((w ** 2).sum())   # unit total variance


def make_source(seed, plant=None):
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2024-01-02", "2025-12-31")
    w = u_shape()
    lv = np.log(0.008); px = 5000.0; prev_close = px; prev_rng = []
    rows_t, rows_o = [], []
    for di, d in enumerate(days):
        lv = 0.9 * lv + 0.1 * np.log(0.008) + 0.18 * rng.standard_normal()     # daily vol regime
        sig = float(np.exp(lv)); sig_on = 0.45 * sig
        on = rng.standard_normal(ON_MIN) * sig_on / np.sqrt(ON_MIN)
        r = rng.standard_normal(RTH_MIN) * sig * w * (1 + 0.1 * rng.standard_t(4, RTH_MIN).clip(-5, 5) ** 2) ** 0.5
        open_px = prev_close * np.exp(on.sum())
        if plant is not None:
            r = plant_edge(plant, r, on, d, open_px, prev_close, prev_rng, sig, w)
        lp = np.log(prev_close) + np.r_[np.cumsum(on), on.sum() + np.cumsum(r)]
        start = (d - pd.Timedelta(days=1 if d.weekday() else 3)).normalize() + pd.Timedelta(hours=18)
        t_on = start + pd.to_timedelta(np.arange(ON_MIN), "min")
        t_rth = d.normalize() + pd.Timedelta(hours=9, minutes=30) + pd.to_timedelta(np.arange(RTH_MIN), "min")
        rows_t.append(np.r_[t_on.values, t_rth.values]); rows_o.append(lp)
        rth_px = np.exp(lp[ON_MIN:]); prev_rng.append(rth_px.max() - rth_px.min())
        prev_close = float(rth_px[-1])
    t = np.concatenate(rows_t); c = np.exp(np.concatenate(rows_o))
    o = np.r_[c[0], c[:-1]]
    noise = np.abs(rng.standard_normal((2, len(c)))) * c * 0.00004
    df = pd.DataFrame(dict(open=o, high=np.maximum(o, c) + noise[0], low=np.minimum(o, c) - noise[1], close=c), index=pd.DatetimeIndex(t))
    return df


def plant_edge(s, r, on, d, open_px, prev_close, prev_rng, sig, w):
    k = s["strength_k"]; kind = s["strategy"]; r = r.copy()

    def drift(i0, i1, direction):           # add k x (segment sd) spread evenly over bars i0..i1-1
        seg_sd = sig * np.sqrt((w[i0:i1] ** 2).sum())
        r[i0:i1] += direction * k * seg_sd / (i1 - i0)

    cum = np.cumsum(r)                       # path before any drift (drift only touches later bars)
    if kind == "orb_continuation" or kind == "narrow_range_breakout":
        n = s["or_minutes"]
        if kind == "narrow_range_breakout":
            if len(prev_rng) < 30 or prev_rng[-1] >= np.median(prev_rng[-60:]):
                return r
        p = open_px * np.exp(cum); hi, lo = p[:n].max(), p[:n].min()
        for j in range(n, RTH_MIN - 30):
            if p[j] > hi or p[j] < lo:
                drift(j + 1, RTH_MIN, 1 if p[j] > hi else -1); break
    elif kind == "gap_fill":
        g = open_px / prev_close - 1
        if abs(g) >= s["min_gap_pct"] / 100:
            # pull back toward prior close in the first 90 minutes (fraction of the gap, capped by strength)
            n = s["fill_minutes"]; seg_sd = sig * np.sqrt((w[:n] ** 2).sum())
            r[:n] += -np.sign(g) * min(k * seg_sd, 0.6 * abs(g)) / n
    elif kind == "power_hour_trend":
        i0 = RTH_MIN - 60; drift(i0, RTH_MIN, np.sign(cum[i0 - 1]))
    elif kind == "weekday_drift":
        if d.weekday() == s["weekday"]:
            drift(0, RTH_MIN, s["direction"])
    elif kind == "lunch_reversal":
        i0, i1 = 150, 270                     # 12:00 -> 14:00 reverses 09:30 -> 12:00
        drift(i0, i1, -np.sign(cum[i0 - 1]))
    elif kind == "overnight_momentum":
        drift(0, 60, np.sign(on.sum()))
    return r


def main():
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(f"{OUT}/secret.json"):
        raise SystemExit("secret already exists; refusing to overwrite")
    s = secret_draw()
    blob = json.dumps(s, sort_keys=True).encode()
    open(f"{OUT}/secret.json", "wb").write(blob)
    seeds = np.random.default_rng(int.from_bytes(os.urandom(8), "little")).integers(1, 2**31, 3)
    for name, seed in zip(SOURCES, seeds):
        df = make_source(int(seed), s if name == s["source"] else None)
        df.to_parquet(f"{OUT}/{name}.parquet")
        print(name, len(df), "bars", df.index[0], "->", df.index[-1])
    print("secret sha256:", hashlib.sha256(blob).hexdigest())


if __name__ == "__main__":
    main()
