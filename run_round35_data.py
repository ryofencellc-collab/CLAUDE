"""python run_round35_data.py SYMBOL -> data/opt/SYMBOL.pkl (+ _earnings.txt, _px.pkl)"""
import sys
from edge import optdata as o
s = sys.argv[1]
o.fetch_symbol(s)
o.underlying(s).to_pickle(o.CACHE / f"{s}_px.pkl")
open(o.CACHE / f"{s}_earnings.txt", "w").write("\n".join(o.earnings(s)))
