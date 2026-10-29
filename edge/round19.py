"""Round 19 (PROTOCOL_ROUND19.md): the Round 18 maker trade on every other daily-temperature series.

Round 18 covered the US daily-high series in round15.STATIONS. This adds daily-low series (US and
international) and the daily-high series Round 18 skipped. Each series ticker ends in a city code;
CODES maps it to (ASOS/METAR station, time zone).
"""
import re

from edge import round15, weather as wx

US = {
    "NY": ("NYC", "America/New_York"), "NYC": ("NYC", "America/New_York"), "CHI": ("MDW", "America/Chicago"),
    "AUS": ("AUS", "America/Chicago"), "DEN": ("DEN", "America/Denver"), "LAX": ("LAX", "America/Los_Angeles"),
    "MIA": ("MIA", "America/New_York"), "PHIL": ("PHL", "America/New_York"), "ATL": ("ATL", "America/New_York"),
    "BOS": ("BOS", "America/New_York"), "DAL": ("DFW", "America/Chicago"), "DC": ("DCA", "America/New_York"),
    "HOU": ("HOU", "America/Chicago"), "KSAN": ("SAN", "America/Los_Angeles"), "SAN": ("SAN", "America/Los_Angeles"),
    "LV": ("LAS", "America/Los_Angeles"), "MIN": ("MSP", "America/Chicago"), "NOLA": ("MSY", "America/Chicago"),
    "OKC": ("OKC", "America/Chicago"), "PHX": ("PHX", "America/Phoenix"), "SATX": ("SAT", "America/Chicago"),
    "SEA": ("SEA", "America/Los_Angeles"), "SFO": ("SFO", "America/Los_Angeles"), "TTN": ("TTN", "America/New_York"),
    "EWR": ("EWR", "America/New_York"),
}
INTL_TZ = {"EBBR": "Europe/Brussels", "LSGG": "Europe/Zurich", "LSSG": "Europe/Zurich", "EHAM": "Europe/Amsterdam",
           "ZSPD": "Asia/Shanghai", "LTFM": "Europe/Istanbul", "EDDF": "Europe/Berlin"}
SKIP = {"KXHIGHTSDF", "KXLOWTSDF", "KXHIGHUS", "HIGHUS", "KXCITIESWEATHER", "KXDVHIGH"}  # ambiguous or multi-city


def resolve(ticker: str):
    """(code, station, tz, kind) for a daily high/low series ticker, or None."""
    m = re.match(r"^(?:KX)?(HIGH|LOW)T?(.+)$", ticker)
    if not m or ticker in SKIP:
        return None
    kind, code = m.group(1).lower(), m.group(2)
    if code in US:
        return (code, *US[code], kind)
    if code in INTL_TZ:
        return (code, "LSGG" if code == "LSSG" else code, INTL_TZ[code], kind)
    if code in wx.MINOR and len(code) == 4:
        return (code, code, wx.MINOR[code][2], kind)
    return None


def round18_universe() -> set[str]:
    return {s[0] for s in wx.daily_high_series() if s[1] in round15.STATIONS}


def universe() -> list[tuple]:
    """[(series, code, station, tz, kind)] for every daily high/low series not covered by Round 18."""
    r = wx._get(f"{wx.KALSHI}/series", {"category": "Climate and Weather"})
    done, out = round18_universe(), []
    for s in r.json().get("series", []):
        if s.get("frequency") != "daily" or s["ticker"] in done:
            continue
        spec = resolve(s["ticker"])
        if spec:
            out.append((s["ticker"], *spec))
    return sorted(out)
