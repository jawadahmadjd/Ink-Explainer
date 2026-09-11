import os
import json
import csv

base_pm = r"d:\Tools of Jawad\25- Ink Explainers\1- Postmartum\1- What Did Ancient Humans Actually Do All Day"
base_fn = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day"

# 1. Check cuts_data.json
cuts_p = os.path.join(base_pm, "cuts_data.json")
with open(cuts_p, "r", encoding="utf-8") as f:
    cdata = json.load(f)

cuts = cdata.get("cuts", [])
print(f"Total PM cuts: {len(cuts)}")

# Find which PM cuts correspond to time 80s to 135s (01:20 to 02:15)
print("\n=== PM CUTS FROM 80s to 135s ===")
for i, c in enumerate(cuts, 1):
    if 80 <= c <= 135:
        m, s = int(c // 60), c % 60
        print(f"PM Cut {i:03d} at {c:.2f}s ({m:02d}:{s:04.1f}) -> frame shot_{i:03d}.jpg")

# Check storyboard_master.csv rows from 80s to 135s
csv_p = os.path.join(base_fn, "storyboard_master.csv")
with open(csv_p, "r", encoding="utf-8") as f:
    rows = list(csv.reader(f))[1:]

print("\n=== STORYBOARD MASTER ROWS 44 to 64 ===")
for r in rows:
    shot_num = int(r[0])
    if 44 <= shot_num <= 65:
        print(f"Final Shot {shot_num:03d} | {r[1]} | VO: {r[2]} | DESC: {r[3][:45]}")

