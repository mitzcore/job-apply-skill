#!/usr/bin/env python3
"""Append an application outcome to applied.csv.
Usage: python3 log.py tailor/<slug>.json STATUS ["note"]
STATUS: SUBMITTED | SKIPPED | FAILED"""
import csv, json, sys, datetime, pathlib
t = json.loads(pathlib.Path(sys.argv[1]).read_text())
status = sys.argv[2] + (f" ({sys.argv[3]})" if len(sys.argv) > 3 else "")
p = pathlib.Path(__file__).parent / "applied.csv"
with open(p, "a", newline="") as f:
    csv.writer(f).writerow([t["slug"], t["co"], t["title"], t.get("pay", ""), status, datetime.datetime.now().strftime("%F %T")])
print("logged", t["co"], status)
