"""One-off: per-city forecast bias for the live weather bot (PROTOCOL_ROUND5.md forward amendment 1)."""
import json
from pathlib import Path

from edge import weather as wx

df = wx.dataset()
d = df.drop_duplicates(["city", "date"]).dropna(subset=["multi", "observed"])
err = (d["observed"] - d["multi"]).groupby(d["city"])
out = {c: {"bias": round(float(e.mean()), 3), "sd": round(float(e.std()), 3), "days": int(e.size)}
       for c, e in err if e.size >= 20}
Path("paper").mkdir(exist_ok=True)
Path("paper/weather_bias.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print(json.dumps(out, indent=1, sort_keys=True))
