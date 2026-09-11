import os
import csv

base_fn = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day"
csv_p = os.path.join(base_fn, "storyboard_master.csv")
with open(csv_p, "r", encoding="utf-8") as f:
    rows = list(csv.reader(f))[1:]

row_map = {int(r[0]): r for r in rows}

print("================================================================================")
print("SHOT BY SHOT COMPARISON: VO vs INTENDED DESC vs ACTUAL PROMPT IN MASTER CSV")
print("================================================================================")
for s in range(44, 66):
    r = row_map[s]
    vo = r[2]
    desc = r[3]
    prompt = r[4]
    
    # Find scene action in prompt
    parts = prompt.split(", ")
    action_parts = [p for p in parts if any(k in p.lower() for k in ["table", "view", "archaeologist", "map", "grid", "timeline", "field", "split", "scientist", "anatomical", "silhouette", "height", "cross-section", "hurdle", "icons", "hunter", "close-up", "macro", "molar", "tooth", "toothbrush"])]
    action_str = action_parts[-1] if action_parts else prompt[-80:]
    
    print(f"Shot {s:03d} | VO: {vo}")
    print(f"  Intended Visual : {desc}")
    print(f"  Prompt Generated: {action_str}")
    print("-" * 80)

